#!/usr/bin/env python3
"""Offline tests for the advisory live-diagnosis provider (no network/EDA)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import live_diagnosis as ld  # noqa: E402
import evidence_package as ep  # noqa: E402
import evaluate_diagnosis as ed  # noqa: E402


class LiveDiagnosisTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.bundle_dir = self.base / "bundle"
        self.result = ep.build_bundle(self.bundle_dir)
        self.bundle = json.loads((self.bundle_dir / "bundle.json").read_text())
        self.prompt = (self.bundle_dir / "prompt.txt").read_text()
        self.gt = json.loads((self.bundle_dir / "gt.json").read_text())
        self.cfg = ld.ModelConfig(url="https://example.invalid/v1/chat/completions",
                                  model="test-model", key_present=False,
                                  timeout_s=2.0, max_attempts=2, min_interval_s=0.0)
        self.valid = ed.deterministic_output(self.bundle)

    def tearDown(self):
        self.tmp.cleanup()

    def _content(self, obj=None):
        obj = obj or self.valid
        return json.dumps({"choices": [{"message": {"content": json.dumps(obj)}}],
                           "usage": {"prompt_tokens": 10, "completion_tokens": 20}})

    def _transport(self, status=200, body=None, headers=None, calls=None):
        def fn(url, payload, hdrs, timeout):
            if calls is not None:
                calls.append({"url": url, "payload": payload, "headers": hdrs})
            return status, (body or self._content()).encode(), headers or {}
        return fn

    def test_provider_config_defaults_and_caps(self):
        with mock.patch.dict(os.environ, {"SATTVA_MODEL_TIMEOUT_SECS": "999",
                                          "SATTVA_MODEL_MAX_ATTEMPTS": "99"}, clear=False):
            c = ld.ModelConfig.from_env()
        self.assertEqual(c.timeout_s, 120.0)
        self.assertEqual(c.max_attempts, 3)

    def test_missing_credentials_skips_without_request(self):
        calls = []
        out = ld.call_model(self.prompt, self.bundle,
                            ld.ModelConfig(url=None, model="m", key_present=False),
                            transport=self._transport(calls=calls))
        self.assertEqual(out["status"], "SKIPPED_NO_CREDENTIALS")
        self.assertEqual(out["execution_kind"], "not_invoked")
        self.assertEqual(calls, [])

    def test_timeout_status_and_no_fabrication(self):
        def boom(*_a, **_k):
            raise TimeoutError("timed out")
        out = ld.call_model(self.prompt, self.bundle, self.cfg, transport=boom,
                            sleep_fn=lambda _s: None)
        self.assertEqual(out["status"], "TIMEOUT")
        self.assertIsNone(out["parsed_output"])

    def test_rate_limit_retry_bounded(self):
        calls = []
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport(429, "{}", {"Retry-After": "0"}, calls),
                            sleep_fn=lambda _s: None)
        self.assertEqual(out["status"], "RATE_LIMITED")
        self.assertEqual(out["retries"], 1)
        self.assertEqual(len(calls), 2)

    def test_connection_failure_status(self):
        def boom(*_a, **_k):
            raise OSError("connection refused")
        out = ld.call_model(self.prompt, self.bundle, self.cfg, transport=boom,
                            sleep_fn=lambda _s: None)
        self.assertEqual(out["status"], "TRANSPORT_ERROR")

    def test_malformed_json(self):
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport(200, "not json"))
        self.assertEqual(out["status"], "MALFORMED_RESPONSE")

    def test_missing_required_fields(self):
        bad = dict(self.valid)
        bad.pop("verification_plan")
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport(200, self._content(bad)))
        self.assertEqual(out["status"], "SCHEMA_INVALID")
        self.assertTrue(out["schema_valid"] is False)

    def test_fabricated_evidence_ref_rejected(self):
        bad = dict(self.valid)
        bad["supporting_evidence"] = [{"ref": "E-99-FAKE", "excerpt": "x"}]
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport(200, self._content(bad)))
        self.assertEqual(out["status"], "REF_FABRICATION")
        self.assertIn("E-99-FAKE", out["reference_validation"]["fabricated"])

    def test_invalid_excerpt_rejected(self):
        bad = dict(self.valid)
        bad["supporting_evidence"] = [{"ref": "E01", "excerpt": "not verbatim"}]
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport(200, self._content(bad)))
        self.assertEqual(out["status"], "REF_FABRICATION")

    def test_fabricated_ref_in_contradicting_evidence_rejected(self):
        bad = dict(self.valid)
        bad["contradicting_evidence"] = [{"ref": "E99", "excerpt": "x"}]
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport(200, self._content(bad)))
        self.assertEqual(out["status"], "REF_FABRICATION")

    def test_grader_hard_gates(self):
        bad = dict(self.valid)
        bad["supporting_evidence"] = [{"ref": "E99", "excerpt": "x"}]
        grade = ed.grade(bad, self.bundle, self.gt)
        self.assertTrue(grade["hard_gates"]["REF_FABRICATION"])
        leak = dict(self.valid)
        leak["primary_hypothesis"] = "RESTORE_MACRO_LIB was approved"
        self.assertTrue(ed.grade(leak, self.bundle, self.gt)["hard_gates"]["GT_LEAK"])

    def test_unstructured_string_refs_not_vacuously_valid(self):
        bad = dict(self.valid)
        bad["supporting_evidence"] = ["E03: make: *** No rule to make target"]
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport(200, self._content(bad)))
        self.assertFalse(out["refs_valid"])
        self.assertTrue(any(r["status"] == "UNRESOLVED"
                            for r in out["reference_validation"]["refs"]))

    def test_string_type_metrics_not_inflated(self):
        bad = dict(self.valid)
        bad["contradicting_evidence"] = "UNKNOWN"
        bad["risk_assessment"] = "one prose sentence"
        g = ed.grade(bad, self.bundle, self.gt)
        self.assertEqual(g["scores"]["contradiction_handling"], "UNSUPPORTED")
        self.assertEqual(g["scores"]["risk_identification"], "UNSUPPORTED")

    def test_credential_redaction(self):
        text = "Authorization: Bearer sk-abcdefghijklmnop key=eyJabcdefghijk"
        red = ld.redact(text, "sk-abcdefghijklmnop")
        self.assertNotIn("sk-abcdefghijklmnop", red)
        self.assertNotIn("eyJabcdefghijk", red)
        self.assertIn("REDACTED", red)

    def test_no_secret_in_telemetry(self):
        calls = []
        cfg = ld.ModelConfig(url=self.cfg.url, model="m", key_present=True)
        with mock.patch.dict(os.environ, {"SATTVA_MODEL_KEY": "sk-supersecretvalue1234"}):
            out = ld.call_model(self.prompt, self.bundle, cfg,
                                transport=self._transport(calls=calls))
        self.assertNotIn("sk-supersecretvalue1234", json.dumps(out))
        self.assertEqual(calls[0]["headers"]["Authorization"], "Bearer sk-supersecretvalue1234")

    def test_execution_kind_labeling(self):
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport())
        self.assertEqual(out["execution_kind"], "stub")

    def test_prompt_hash_stability(self):
        a = ep.build_bundle(self.bundle_dir)
        b = ep.build_bundle(self.bundle_dir)
        self.assertEqual(a["prompt_sha256"], b["prompt_sha256"])
        self.assertEqual(a["bundle_sha256"], b["bundle_sha256"])

    def test_no_gt_leak_in_prompt(self):
        for token in ("RESTORE_MACRO_LIB", "AP-PNR-003", "proposal.json",
                      "orfs_baseline_recovered"):
            self.assertNotIn(token.lower(), self.prompt.lower())

    def test_gt_file_separate(self):
        self.assertTrue((self.bundle_dir / "gt.json").exists())
        self.assertNotIn("gt.json", json.dumps(self.bundle))

    def test_deterministic_grade(self):
        grade = ed.grade(self.valid, self.bundle, self.gt)
        self.assertTrue(grade["diagnosis_accepted"])
        self.assertTrue(all(v == "CORRECT" for v in grade["scores"].values()))

    def test_grade_determinism(self):
        a = ed.grade(self.valid, self.bundle, self.gt)
        permuted = dict(reversed(list(self.valid.items())))
        b = ed.grade(permuted, self.bundle, self.gt)
        self.assertEqual(a["scores"], b["scores"])

    def test_no_execution_authority(self):
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport())
        self.assertNotIn("apply", out)
        self.assertNotIn("execute", out)

    def test_token_usage_recorded_when_available(self):
        out = ld.call_model(self.prompt, self.bundle, self.cfg,
                            transport=self._transport())
        self.assertEqual(out["token_usage"]["prompt_tokens"], 10)
        self.assertEqual(out["status"], "OK")


if __name__ == "__main__":
    unittest.main()
