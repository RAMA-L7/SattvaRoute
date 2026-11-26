#!/usr/bin/env python3
"""Phase 7: frozen diagnosis-evaluation v2."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import evaluate_diagnosis_v2 as v2  # noqa: E402

# v1 remains available and unchanged
import evaluate_diagnosis as v1  # noqa: E402


def _bundle(entries):
    return {"bundle_id": "T", "entries": [
        {"id": eid, "text": text, "excerpt_sha256":
         __import__("hashlib").sha256(text.encode()).hexdigest()}
        for eid, text in entries]}


def _model_output(**kw):
    base = dict(
        failure_class="missing macro LEF reference",
        failed_stage="floorplan",
        primary_hypothesis="ADDITIONAL_LEFS references a nonexistent macro LEF",
        supporting_evidence=[{"ref": "E01", "excerpt": kw.pop("e01", "")}],
        contradicting_evidence=[],
        alternative_hypotheses=[],
        confidence="high",
        proposed_action="restore pinned macro LEF",
        patch_candidate="restore ADDITIONAL_LEFS",
        expected_effect="floorplan resolves macro",
        affected_stages=["floorplan", "place", "cts", "route", "finish"],
        risk_assessment=[],
        verification_plan=["scratch test", "isolated rerun"],
        missing_information=[],
    )
    base.update(kw)
    return base


class V1Preserved(unittest.TestCase):
    def test_v1_unchanged_and_separate(self):
        self.assertEqual(v1.ANCHORS["CORRECT"], 3)
        self.assertEqual(v2.RUBRIC_VERSION, "t1_rubric/v2")
        self.assertNotEqual(v2.RUBRIC_VERSION, "t1_rubric/v1")


class CorrectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name) / "config.mk"
        self.original = "export ADDITIONAL_LEFS = $(PLATFORM_DIR)/lef/fakeram45_64x32.lef\n"
        self.target.write_text(self.original + "export ADDITIONAL_LEFS = /x/missing.lef\n",
                               encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_prompt_text_frozen(self):
        self.assertEqual(v2.PROMPT_TEXT,
                         "Propose a textual correction for review; do not execute or apply it.")

    def test_valid_repair_detected_with_scratch(self):
        diff = ("--- " + str(self.target) + "\n+++ " + str(self.target) + "\n"
                "@@ -1,2 +1,2 @@\n"
                " export ADDITIONAL_LEFS = $(PLATFORM_DIR)/lef/fakeram45_64x32.lef\n"
                "-export ADDITIONAL_LEFS = /x/missing.lef\n"
                "+export ADDITIONAL_LEFS = $(PLATFORM_DIR)/lef/fakeram45_64x32.lef\n")
        prop = {"status": "proposal", "applies": False,
                "target_file": str(self.target), "variable": "ADDITIONAL_LEFS",
                "operation": "replace", "intended_value": "$(PLATFORM_DIR)/lef/fakeram45_64x32.lef",
                "exact_diff": diff, "patch": diff,
                "earliest_affected_stage": "floorplan",
                "downstream_invalidation": ["floorplan", "place", "cts", "route", "finish"]}
        before = self.target.read_text(encoding="utf-8")
        corr = v2.validate_correction(prop, _bundle([("E01", "x")]),
                                       {"target_file": str(self.target),
                                        "intended_value": "$(PLATFORM_DIR)/lef/fakeram45_64x32.lef",
                                        "affected_stages": ["floorplan", "place", "cts", "route", "finish"]})
        self.assertTrue(corr["checks"]["target"], corr)
        self.assertTrue(corr["checks"]["downstream"], corr)
        self.assertTrue(corr["scratch_test"].get("applied"), corr["scratch_test"])
        # real target untouched by scratch test
        self.assertEqual(self.target.read_text(encoding="utf-8"), before)

    def test_justified_abstention_distinct_from_repair(self):
        prop = {"status": "insufficient_evidence", "applies": False,
                "reason": "no compatible collateral can be shown to exist",
                "evidence_refs": ["E01"]}
        corr = v2.validate_correction(prop, _bundle([("E01", "x")]), None)
        self.assertEqual(corr["status"], "justified_abstention")
        self.assertTrue(corr["justified_abstention"])
        self.assertFalse(corr["correct_repair"])

    def test_unsupported_abstention(self):
        corr = v2.validate_correction({"status": "insufficient_evidence"}, _bundle([]), None)
        self.assertEqual(corr["status"], "unsupported_abstention")

    def test_unrelated_change_rejected(self):
        diff = ("--- x\n+++ x\n@@\n"
                "-export ADDITIONAL_LEFS = a\n+export ADDITIONAL_LEFS = b\n"
                "+export FOO = bar\n")
        prop = {"target_file": str(self.target), "variable": "ADDITIONAL_LEFS",
                "operation": "replace", "intended_value": "b", "exact_diff": diff,
                "earliest_affected_stage": "floorplan",
                "downstream_invalidation": v2.DOWNSTREAM}
        corr = v2.validate_correction(prop, _bundle([]), None)
        self.assertIn("unrelated change in scope", corr["problems"])

    def test_broad_deletion_rejected(self):
        diff = "--- x\n+++ x\n@@\n" + "".join(f"-line{i}\n" for i in range(5))
        prop = {"target_file": str(self.target), "variable": "ADDITIONAL_LEFS",
                "operation": "replace", "intended_value": "x", "exact_diff": diff,
                "earliest_affected_stage": "floorplan", "downstream_invalidation": v2.DOWNSTREAM}
        corr = v2.validate_correction(prop, _bundle([]), None)
        self.assertIn("broad deletion rejected", corr["problems"])

    def test_constraint_relaxation_rejected(self):
        diff = "--- x\n+++ x\n@@\n-set_false_path -from a\n+set_false_path -from a -to b\n"
        prop = {"target_file": str(self.target), "variable": "SDC",
                "operation": "replace", "intended_value": "x", "exact_diff": diff,
                "earliest_affected_stage": "synth", "downstream_invalidation": v2.DOWNSTREAM}
        corr = v2.validate_correction(prop, _bundle([]), None)
        self.assertIn("constraint relaxation rejected", corr["problems"])

    def test_incorrect_corner_rejected(self):
        prop = {"target_file": str(self.target), "variable": "LIB_FILES",
                "operation": "replace", "intended_value": "nom_voltage : 0.9; ff corner",
                "exact_diff": "@@\n-x\n+y\n", "earliest_affected_stage": "synth",
                "downstream_invalidation": v2.DOWNSTREAM}
        corr = v2.validate_correction(prop, _bundle([]), None)
        self.assertTrue(any("corner" in p for p in corr["problems"]), corr["problems"])

    def test_missing_downstream_rejected(self):
        prop = {"target_file": str(self.target), "variable": "ADDITIONAL_LEFS",
                "operation": "replace", "intended_value": "x", "exact_diff": "@@\n-a\n+b\n",
                "earliest_affected_stage": "floorplan", "downstream_invalidation": ["floorplan"]}
        corr = v2.validate_correction(prop, _bundle([]), None)
        self.assertFalse(corr["checks"]["downstream"])


class GradeTests(unittest.TestCase):
    def test_schema_and_reference_separate_from_engineering(self):
        e01 = "No rule to make target '/x/missing.lef', needed by 'y'. Stop."
        bundle = _bundle([("E01", e01), ("E02", "synth\t0\ts\te"), ("E03", "x"), ("E04", "x"), ("E05", "x"), ("E06", "x")])
        out = _model_output(e01=e01, failed_stage="floorplan")
        res = v2.grade(out, bundle, None)
        self.assertTrue(res["schema_valid"], res["schema_errors"])
        self.assertEqual(res["rubric_version"], v2.RUBRIC_VERSION)
        self.assertIn("schema_valid", res)
        self.assertIn("references_valid", res)
        self.assertIn("engineering_correctness", res)
        # a keyword in serialized output does not imply correctness
        self.assertFalse(res["correct_repair"])

    def test_no_filler_required(self):
        # empty risk_assessment / alternatives / missing_information accepted
        e01 = "No rule to make target '/x.lef'. Stop."
        bundle = _bundle([("E01", e01), ("E02", "x"), ("E03", "x"), ("E04", "x"), ("E05", "x"), ("E06", "x")])
        out = _model_output(e01=e01, risk_assessment=[], alternative_hypotheses=[],
                            missing_information=[])
        res = v2.grade(out, bundle, None)
        self.assertEqual(res["scores"]["no_filler_required"], "CORRECT")


if __name__ == "__main__":
    unittest.main(verbosity=2)
