#!/usr/bin/env python3
"""Negative tests for evidence-to-verdict qualification (offline, no EDA)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import evaluate_diagnosis_v3 as v3  # noqa: E402
import timing_audit as ta  # noqa: E402
from verify_run import FAIL, UNKNOWN, verify_recovery, verify_run  # noqa: E402
from test_verify_run import bound_audit, make_run  # noqa: E402


def raw_audit(*, drop: str | None = None, section_error: str | None = None,
              truncated: bool = False, clock: str = "clk 1.0 0.0 0.5") -> str:
    names = ["LIBERTY", "LOAD", "RC_CORNER", "SPEF", "UPDATE_TIMING",
             "REPORT_UNITS", "CLOCK_PROPERTIES", "WORST_SLACK", "CHECK_SETUP",
             "PARASITICS", "COVERAGE", "UNCONSTRAINED"]
    parts = []
    for name in names:
        parts.append(f"===== {name} =====")
        if name == "REPORT_UNITS":
            parts.append("time 1ns")
        elif name == "CLOCK_PROPERTIES":
            parts.append(clock)
        elif name == "WORST_SLACK":
            parts.append("worst slack max 0.64")
        elif name == "COVERAGE":
            parts += ["input_ports 73", "output_ports 32", "registers 1", "clocks 1"]
        elif name == "UNCONSTRAINED":
            parts += ["Startpoint: a", "Endpoint: b", "Startpoint: c", "Endpoint: d"]
        if section_error and name == section_error:
            parts.append(f"SECTION_ERROR {name}: boom")
        if name != drop:
            parts.append(f"SECTION_OK {name}")
    if section_error:
        parts.append(f"SECTION_ERROR {section_error}: boom")
    if not truncated:
        parts += ["AUDIT_STATUS OK errors=0", "===== AUDIT_DONE ====="]
    return "\n".join(parts) + "\n"


class TimingAuditTests(unittest.TestCase):
    def test_complete_stream_is_complete(self):
        parsed = ta.parse(raw_audit())
        self.assertTrue(parsed["audit_complete"])
        self.assertEqual(parsed["coverage"]["unconstrained_endpoints"], 0)
        self.assertEqual(parsed["coverage"]["unconstrained_report_lines"], 2)
        self.assertEqual(parsed["clock"]["period"], 1.0)

    def test_missing_section_is_not_pass(self):
        parsed = ta.parse(raw_audit(drop="CHECK_SETUP"))
        self.assertFalse(parsed["audit_complete"])
        self.assertFalse(parsed["coverage"]["check_setup_completed"])
        self.assertFalse(parsed["audit_complete"])

    def test_no_coverage_sections_means_unknown_endpoints(self):
        text = "\n".join(ln for ln in raw_audit().splitlines()
                         if "SECTION_OK CHECK_SETUP" not in ln
                         and "SECTION_OK UNCONSTRAINED" not in ln)
        parsed = ta.parse(text)
        self.assertIsNone(parsed["coverage"]["unconstrained_endpoints"])

    def test_section_error_is_recorded_and_fails_closed(self):
        parsed = ta.parse(raw_audit(section_error="UPDATE_TIMING"))
        self.assertFalse(parsed["audit_complete"])
        self.assertTrue(parsed["section_errors"])

    def test_truncated_output_is_incomplete(self):
        parsed = ta.parse(raw_audit(truncated=True))
        self.assertFalse(parsed["audit_complete"])

    def test_warning_lines_are_not_endpoint_counts(self):
        raw = raw_audit().replace("===== CHECK_SETUP =====\n",
                                  "===== CHECK_SETUP =====\nfoo bar warning\n")
        parsed = ta.parse(raw)
        self.assertIsNone(parsed["coverage"]["unconstrained_endpoints"])
        self.assertEqual(parsed["coverage"]["check_setup_warnings"], ["foo bar warning"])

    def test_non_finite_clock_is_unknown_not_zero(self):
        parsed = ta.parse(raw_audit(clock="clk nan 0.0 0.5"))
        self.assertIsNone(parsed["clock"])


class VerifierBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def status(self, run, audit=None):
        return verify_run(run, bound_audit(run) if audit is None else audit)

    def check(self, out, name):
        return next(c for c in out["checks"] if c["name"] == name)["status"]

    def test_wrong_run_audit_is_rejected(self):
        run = make_run(self.root, name="run")
        audit = bound_audit(run)
        audit["binding"]["run_id"] = "another-run"
        out = self.status(run, audit)
        self.assertEqual(self.check(out, "audit_binding"), FAIL)
        self.assertEqual(out["overall"], FAIL)

    def test_tampered_final_sdc_is_rejected(self):
        run = make_run(self.root, name="run")
        audit = bound_audit(run)
        (run / "work" / "results" / "nangate45" / "design" / "base" /
         "6_final.sdc").write_text("create_clock -period 2 [get_ports clk]\n")
        out = self.status(run, audit)
        self.assertEqual(self.check(out, "audit_binding"), FAIL)

    def test_non_finite_clock_cannot_pass(self):
        run = make_run(self.root, name="run")
        audit = bound_audit(run)
        audit["clock"]["period"] = float("nan")
        out = self.status(run, audit)
        self.assertEqual(self.check(out, "timing"), UNKNOWN)

    def test_missing_clock_period_file_is_unknown(self):
        run = make_run(self.root, name="run")
        (run / "work" / "results" / "nangate45" / "design" / "base" /
         "clock_period.txt").unlink()
        out = self.status(run)
        self.assertEqual(self.check(out, "timing"), UNKNOWN)

    def test_early_zero_then_final_violation_fails(self):
        run = make_run(self.root, name="run", drt_counts=(0, 0, 3))
        out = self.status(run)
        self.assertEqual(self.check(out, "routing"), FAIL)

    def test_forged_apply_record_fails(self):
        base = self.status(make_run(self.root, name="base"))
        fail = verify_run(make_run(self.root, name="fail", stages_rc=2,
                                   artifacts=False, drt_counts=()), None)
        rec = self.status(make_run(self.root, name="rec"))
        apply = {"phase": "verified", "after_sha256": "a" * 64,
                 "rerun_scope": ["synth"], "target": "config.mk"}
        out = verify_recovery(base, fail, rec, approval_apply=apply)
        self.assertEqual(next(c["status"] for c in out["checks"]
                              if c["name"] == "approved_change_reached"), FAIL)

    def test_failure_marker_must_exist(self):
        base = self.status(make_run(self.root, name="base"))
        fail = verify_run(make_run(self.root, name="fail", stages_rc=2,
                                   artifacts=False, drt_counts=()), None)
        rec = self.status(make_run(self.root, name="rec"))
        out = verify_recovery(base, fail, rec, targeted_marker="missing_fakeram")
        self.assertEqual(next(c["status"] for c in out["checks"]
                              if c["name"] == "failure_marker_present"), FAIL)


class IdentityV3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name) / "config.mk"
        self.target.write_text("export ADDITIONAL_LEFS = old\n", encoding="utf-8")
        self.gt = {"target_file": str(self.target), "intended_value": "new",
                   "design_root": str(self.target.parent),
                   "allowed_roots": [str(self.target.parent)],
                   "affected_stages": ["floorplan", "place", "cts", "route", "finish"]}
        self.bundle = {"entries": []}

    def tearDown(self):
        self.tmp.cleanup()

    def prop(self, **kw):
        diff = ("--- " + str(self.target) + "\n+++ " + str(self.target) + "\n"
                "@@ -1 +1 @@\n-export ADDITIONAL_LEFS = old\n"
                "+export ADDITIONAL_LEFS = new\n")
        out = {"status": "proposal", "applies": False, "target_file": str(self.target),
               "variable": "ADDITIONAL_LEFS", "operation": "replace",
               "intended_value": "new", "exact_diff": diff,
               "earliest_affected_stage": "floorplan",
               "downstream_invalidation": ["floorplan", "place", "cts", "route", "finish"]}
        out.update(kw)
        return out

    def test_wrong_root_same_basename_rejected(self):
        other = Path(self.tmp.name) / "other" / "config.mk"
        other.parent.mkdir()
        corr = v3.strict_validate_correction(self.prop(target_file=str(other)),
                                             self.bundle, self.gt)
        self.assertIn("exact canonical approved target", " ".join(corr["problems"]))

    def test_suffix_replacement_rejected(self):
        prop = self.prop()
        prop["intended_value"] = "new_extra"
        corr = v3.strict_validate_correction(prop, self.bundle, self.gt)
        self.assertIn("exact match", " ".join(corr["problems"]))

    def test_corner_token_rejected(self):
        prop = self.prop()
        prop["intended_value"] = "$(PLATFORM_DIR)/lib/ff/fakeram45_64x32.lib"
        corr = v3.strict_validate_correction(prop, self.bundle, self.gt)
        self.assertTrue(any("corner" in p for p in corr["problems"]))

    def test_unrelated_variable_rejected(self):
        prop = self.prop()
        prop["exact_diff"] += "+export FOO = bar\n"
        corr = v3.strict_validate_correction(prop, self.bundle, self.gt)
        self.assertTrue(any("target variable assignment" in p for p in corr["problems"]))

    def test_missing_variable_rejected(self):
        prop = self.prop()
        prop.pop("variable")
        corr = v3.strict_validate_correction(prop, self.bundle, self.gt)
        self.assertTrue(any("mandatory" in p for p in corr["problems"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
