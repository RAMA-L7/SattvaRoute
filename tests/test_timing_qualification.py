#!/usr/bin/env python3
"""Negative/positive tests for timing qualification binding and numeric comparison."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import verify_run as vr  # noqa: E402
from test_verify_run import make_run  # noqa: E402


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        cfg = json.loads((ROOT / "config" / "sattva_manifest.json").read_text())
        self.cfg = cfg
        self.profile = "nangate_macro_control"
        self.platform = cfg["profiles"][self.profile]["platform_files"]
        self.tool_hash = cfg["tools"]["openroad"]["expected_sha256"]
        self.orfs = cfg["orfs"]["revision"]

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, run: Path, *, prefix="qual", metrics=None, capability="AVAILABLE"):
        res = run / "work" / "results" / "nangate45" / "design" / "base"
        ev = run / "evidence"
        ev.mkdir(parents=True, exist_ok=True)
        (ev / "manifest.json").write_text(json.dumps({"digest": "d", "fingerprint": "tq-fp"}))
        run_doc = json.loads((ev / "run.json").read_text(encoding="utf-8"))
        run_doc["active_profile"] = self.profile
        (ev / "run.json").write_text(json.dumps(run_doc), encoding="utf-8")
        raw = self.root / f"{prefix}.raw.txt"
        raw.write_text("CAPABILITY_AVAILABLE sta_find_timing\n"
                       "SECTION_OK TIMING_UPDATE\n"
                       "AUDIT_STATUS OK errors=0\n"
                       "===== AUDIT_DONE =====\n"
                       "timing raw output\n")
        m = {"wns": 0.0, "tns": 0.0, "worst_slack_max": 0.64, "worst_slack_min": 0.08,
             "clock_period": 1000.0, "timing_paths": 1, "unconstrained_paths": 0,
             "unannotated_drivers": 0, "partially_unannotated_drivers": 0}
        if metrics:
            m.update(metrics)
        q = {
            "schema": "timing_qualification/v1",
            "run_id": run.name,
            "active_profile": self.profile,
            "raw_output": str(raw),
            "binding": {
                "design_fingerprint": "tq-fp",
                "orfs_revision": self.orfs,
                "opensta_revision": "UNKNOWN",
                "sdc_sha256": sha((res / "6_final.sdc").read_bytes()),
                "liberty_std_sha256": self.platform["lib/NangateOpenCellLibrary_typical.lib"],
                "liberty_macro_sha256": self.platform["lib/fakeram45_64x32.lib"],
                "rc_set_sha256": self.platform["setRC.tcl"],
                "rcx_rules_sha256": self.platform["rcx_patterns.rules"],
                "spef_sha256": sha((res / "6_final.spef").read_bytes()),
                "odb_sha256": sha((res / "6_final.odb").read_bytes()),
                "tool": {"id": "openroad", "version": "bazel-nostamp",
                         "exe_sha256": self.tool_hash,
                         "invocation": "::sta::find_timing -full_update"},
                "raw_output_sha256": sha(raw.read_bytes()),
            },
            "capability": {"id": "sta_find_timing",
                           "invocation": "::sta::find_timing -full_update",
                           "available": capability == "AVAILABLE",
                           "rc": 0, "status": capability},
            "metrics": m,
            "status": "PASS" if capability == "AVAILABLE" else "UNKNOWN",
        }
        return q

    def test_valid_qualification_binds_and_passes(self):
        run = make_run(self.root, name="run")
        q = self.make(run)
        view = vr.load_run(run)
        self.assertIsNone(vr.qualification_binding_error(view, q))
        out = vr.check_timing_qualification(view, q)
        self.assertEqual(out.status, vr.PASS, out.detail)

    def test_wrong_tool_hash_rejected(self):
        run = make_run(self.root, name="run")
        q = self.make(run)
        q["binding"]["tool"]["exe_sha256"] = "0" * 64
        self.assertIn("tool identity", vr.qualification_binding_error(vr.load_run(run), q))

    def test_wrong_profile_rejected(self):
        run = make_run(self.root, name="run")
        q = self.make(run)
        q["active_profile"] = "sattva_sram"
        self.assertIn("profile", str(vr.qualification_binding_error(vr.load_run(run), q)))

    def test_wrong_run_rejected(self):
        run = make_run(self.root, name="run")
        q = self.make(run)
        q["run_id"] = "another-run"
        self.assertIn("run_id", vr.qualification_binding_error(vr.load_run(run), q))

    def test_tampered_timing_input_rejected(self):
        run = make_run(self.root, name="run")
        q = self.make(run)
        q["binding"]["sdc_sha256"] = "f" * 64
        self.assertIn("artifact hash", vr.qualification_binding_error(vr.load_run(run), q))

    def test_tampered_raw_output_rejected(self):
        run = make_run(self.root, name="run")
        q = self.make(run)
        (self.root / "qual.raw.txt").write_text("tampered\n")
        self.assertIn("raw output hash", vr.qualification_binding_error(vr.load_run(run), q))

    def test_unavailable_capability_is_unknown(self):
        run = make_run(self.root, name="run")
        q = self.make(run, capability="UNAVAILABLE", prefix="nocap")
        out = vr.check_timing_qualification(vr.load_run(run), q)
        self.assertEqual(out.status, vr.UNKNOWN, out.detail)

    def test_non_finite_metric_is_unknown(self):
        run = make_run(self.root, name="run")
        q = self.make(run, prefix="nan", metrics={"wns": float("nan")})
        out = vr.check_timing_qualification(vr.load_run(run), q)
        self.assertEqual(out.status, vr.UNKNOWN, out.detail)

    def test_numeric_comparison_passes_identical(self):
        run = make_run(self.root, name="run")
        q1 = self.make(run, prefix="a")
        q2 = self.make(run, prefix="b")
        q2["run_id"] = "recovery"
        out = vr.compare_timing_qualifications(q1, q2)
        self.assertEqual(out.status, vr.PASS, out.detail)

    def test_numeric_regression_fails(self):
        run = make_run(self.root, name="run")
        q1 = self.make(run, prefix="a")
        q2 = self.make(run, prefix="b", metrics={"wns": -0.5})
        q2["run_id"] = "recovery"
        out = vr.compare_timing_qualifications(q1, q2)
        self.assertEqual(out.status, vr.FAIL, out.detail)

    def test_missing_qualification_is_not_evaluated(self):
        out = vr.compare_timing_qualifications(None, None)
        self.assertEqual(out.status, vr.NOT_EVALUATED, out.detail)

    def test_unknown_status_never_upgraded(self):
        run = make_run(self.root, name="run")
        q = self.make(run, capability="UNAVAILABLE", prefix="unknown")
        out = vr.check_timing_qualification(vr.load_run(run), q)
        self.assertEqual(out.status, vr.UNKNOWN, out.detail)

    def test_required_qualification_missing_is_unknown(self):
        out = vr.compare_timing_qualifications(None, None, required=True)
        self.assertEqual(out.status, vr.UNKNOWN, out.detail)

    def test_profile_from_manifest_is_enforced(self):
        run = make_run(self.root, name="run")
        q = self.make(run)
        ev = run / "evidence"
        run_doc = json.loads((ev / "run.json").read_text())
        run_doc.pop("active_profile", None)
        (ev / "run.json").write_text(json.dumps(run_doc))
        (ev / "manifest.json").write_text(json.dumps(
            {"digest": "d", "fingerprint": "tq-fp", "profile": self.profile}))
        q["active_profile"] = "sattva_sram"
        self.assertIn("profile", str(vr.qualification_binding_error(vr.load_run(run), q)))

    def test_forged_capability_identity_rejected(self):
        run = make_run(self.root, name="run")
        q = self.make(run)
        q["capability"]["id"] = "NOT_sta_find_timing"
        q["capability"]["invocation"] = "bogus"
        out = vr.check_timing_qualification(vr.load_run(run), q)
        self.assertEqual(out.status, vr.FAIL, out.detail)

    def test_raw_tamper_with_updated_hash_rejected(self):
        run = make_run(self.root, name="run")
        q = self.make(run)
        raw = Path(q["raw_output"])
        raw.write_text("tampered output\n")
        q["binding"]["raw_output_sha256"] = sha(raw.read_bytes())
        out = vr.check_timing_qualification(vr.load_run(run), q)
        self.assertEqual(out.status, vr.FAIL, out.detail)

    def test_negative_metrics_rejected(self):
        run = make_run(self.root, name="run")
        q = self.make(run, metrics={"wns": -1.0, "tns": -1.0})
        out = vr.check_timing_qualification(vr.load_run(run), q)
        self.assertEqual(out.status, vr.FAIL, out.detail)

    def test_compare_rejects_tool_mismatch(self):
        run = make_run(self.root, name="run")
        q1 = self.make(run, prefix="a")
        q2 = self.make(run, prefix="b")
        q2["run_id"] = "recovery"
        q2["binding"]["tool"]["exe_sha256"] = "0" * 64
        out = vr.compare_timing_qualifications(q1, q2)
        self.assertEqual(out.status, vr.UNKNOWN, out.detail)

    def test_missing_count_metric_is_unknown(self):
        run = make_run(self.root, name="run")
        q = self.make(run, prefix="nocount")
        q["metrics"].pop("unconstrained_paths")
        out = vr.check_timing_qualification(vr.load_run(run), q)
        self.assertEqual(out.status, vr.UNKNOWN, out.detail)


if __name__ == "__main__":
    unittest.main(verbosity=2)
