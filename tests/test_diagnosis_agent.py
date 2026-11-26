#!/usr/bin/env python3
"""Phase 6: generalized bounded diagnosis + reviewable proposal."""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import diagnosis_agent as da  # noqa: E402

CONTROL = ROOT / "benchmark" / "design" / "nangate_macro_control"
MIRROR = ROOT / "tools" / "OpenROAD-flow-scripts"


class ParseTests(unittest.TestCase):
    def test_multiline_and_multiple_values(self):
        text = (
            "export ADDITIONAL_LEFS = a.lef \\\n  b.lef c.lef\n"
            "export X = p \\\nq r\n"
            "Y += extra\n"
            "Z ?= fallback\n"
            "W := fixed\n"
        )
        a = {x.var: x for x in da.parse_make_assignments(text)}
        self.assertEqual(a["ADDITIONAL_LEFS"].value, "a.lef b.lef c.lef")
        self.assertEqual(a["X"].value, "p q r")
        self.assertEqual(a["Y"].op, "+=")
        self.assertEqual(a["Z"].op, "?=")
        self.assertEqual(a["W"].op, ":=")

    def test_split_values(self):
        self.assertEqual(da._split_values("a.lef b.lef  c.lef"), ["a.lef", "b.lef", "c.lef"])


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name) / "run"
        (self.run / "evidence").mkdir(parents=True)
        (self.run / "evidence" / "run.json").write_text("{}\n")
        (self.run / "evidence" / "stages.tsv").write_text(
            "synth\t0\ts\te\nfloorplan\t2\ts\te\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_macro_lef_not_dependent_on_injected_name(self):
        # a *different* nonexistent name, different declaration structure
        (self.run / "evidence" / "stage_floorplan.log").write_text(
            "[ERROR] cannot open lef file /mnt/x/attempt-local/widget_macro.lef: "
            "No such file or directory\n")
        d = da.classify_failure(self.run)
        self.assertEqual(d["family"], da.MISSING_MACRO_LEF)
        self.assertEqual(d["failed_stage"], "floorplan")
        self.assertTrue(any("widget_macro.lef" in m for m in d["missing_references"]))
        self.assertNotIn("missing_fakeram", json_safe(d))

    def test_missing_constraint(self):
        (self.run / "evidence" / "stage_synth.log").write_text(
            "read_sdc: No such file or directory: constraints/missing.sdc\n")
        d = da.classify_failure(self.run)
        self.assertEqual(d["family"], da.MISSING_CONSTRAINT)
        self.assertEqual(d["affected_variable"], "SDC_FILE")

    def test_does_not_require_injected_missing_name(self):
        (self.run / "evidence" / "stage_floorplan.log").write_text(
            "No rule to make target '/x/lef/not_a_real_macro.lef', needed by 'x'. Stop.\n")
        d = da.classify_failure(self.run)
        self.assertEqual(d["family"], da.MISSING_MACRO_LEF)
        self.assertEqual(d["missing_file"], "/x/lef/not_a_real_macro.lef")


def json_safe(d) -> str:
    import json
    return json.dumps(d)


class ProposeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.design = self.base / "attempt" / "design"
        (self.design / "rtl").mkdir(parents=True)
        (self.design / "netlist").mkdir(parents=True)
        shutil.copy2(CONTROL / "constraint.sdc", self.design / "constraint.sdc")
        shutil.copytree(CONTROL / "rtl", self.design / "rtl", dirs_exist_ok=True)
        shutil.copytree(CONTROL / "netlist", self.design / "netlist", dirs_exist_ok=True)
        self.cfg = self.design / "config.mk"
        self.original = (CONTROL / "config.mk").read_text(encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, extra: str):
        self.cfg.write_text(self.original + "\n" + extra + "\n", encoding="utf-8")

    def test_restores_additional_lefs_from_baseline(self):
        self._write("export ADDITIONAL_LEFS = /nonexistent/widget_macro.lef")
        diag = {"family": da.MISSING_MACRO_LEF, "failed_stage": "floorplan",
                "missing_file": "/nonexistent/widget_macro.lef",
                "affected_variable": "ADDITIONAL_LEFS", "evidence_refs": []}
        prop = da.propose_patch(diag, self.cfg, baseline=CONTROL, mirror=MIRROR)
        self.assertIsNotNone(prop)
        self.assertEqual(prop["status"], "proposal")
        self.assertFalse(prop["applies"])
        self.assertEqual(prop["variable"], "ADDITIONAL_LEFS")
        self.assertIn("ADDITIONAL_LEFS", prop["exact_diff"])
        self.assertEqual(prop["intended_value"], "$(PLATFORM_DIR)/lef/fakeram45_64x32.lef")
        self.assertTrue(Path(prop["intended_value_resolved"]).is_file())
        self.assertEqual(prop["patch_sha256"], da.sha256_text(prop["exact_diff"]))
        self.assertEqual(prop["target_original_hash"], da.sha256_file(self.cfg))
        self.assertEqual(prop["earliest_affected_stage"], "floorplan")
        self.assertEqual(prop["downstream_invalidation"],
                         ["floorplan", "place", "cts", "route", "finish"])
        self.assertIn("requires_human_approval", prop)
        self.assertTrue(prop["requires_human_approval"])
        self.assertIn("do not execute or apply", prop["note"].lower())
        self.assertTrue(prop["risks"])
        self.assertTrue(prop["verification_criteria"])
        self.assertTrue(prop["current_resolved_value"])
        # original untouched
        self.assertEqual(self.cfg.read_text(encoding="utf-8"),
                         self.original + "\nexport ADDITIONAL_LEFS = /nonexistent/widget_macro.lef\n")

    def test_restores_additional_libs_from_baseline(self):
        self._write("export ADDITIONAL_LIBS = /nonexistent/macro_model.lib")
        diag = {"family": da.MISSING_MACRO_LIB, "failed_stage": "synth",
                "missing_file": "/nonexistent/macro_model.lib",
                "affected_variable": "ADDITIONAL_LIBS", "evidence_refs": []}
        prop = da.propose_patch(diag, self.cfg, baseline=CONTROL, mirror=MIRROR)
        self.assertIsNotNone(prop)
        self.assertEqual(prop["intended_value"], "$(PLATFORM_DIR)/lib/fakeram45_64x32.lib")

    def test_unsupported_make_construct_is_rejected(self):
        self._write("export ADDITIONAL_LEFS = $(shell echo /x.lef)")
        diag = {"family": da.MISSING_MACRO_LEF, "failed_stage": "floorplan",
                "missing_file": "/x.lef", "affected_variable": "ADDITIONAL_LEFS",
                "evidence_refs": []}
        prop = da.propose_patch(diag, self.cfg, baseline=CONTROL, mirror=MIRROR)
        self.assertEqual(prop["status"], da.INSUFFICIENT)
        self.assertFalse(prop["applies"])
        self.assertIn("unsupported Make construct", prop["reason"])

    def test_ambiguous_replacement_is_insufficient(self):
        # no compatible baseline and no existing collateral anywhere
        empty_baseline = self.base / "empty_baseline"
        empty_baseline.mkdir()
        empty_mirror = self.base / "empty_mirror"
        empty_mirror.mkdir()
        self._write("export ADDITIONAL_LEFS = /nonexistent/widget_macro.lef")
        diag = {"family": da.MISSING_MACRO_LEF, "failed_stage": "floorplan",
                "missing_file": "/nonexistent/widget_macro.lef",
                "affected_variable": "ADDITIONAL_LEFS", "evidence_refs": []}
        prop = da.propose_patch(diag, self.cfg, baseline=empty_baseline,
                                mirror=empty_mirror)
        self.assertEqual(prop["status"], da.INSUFFICIENT)
        self.assertFalse(prop["applies"])
        self.assertIn("refusing to invent", prop["reason"])

    def test_no_bounded_rule_returns_none(self):
        prop = da.propose_patch({"family": "PIN_ACCESS"}, self.cfg,
                                baseline=CONTROL, mirror=MIRROR)
        self.assertIsNone(prop)


if __name__ == "__main__":
    unittest.main(verbosity=2)
