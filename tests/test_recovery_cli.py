#!/usr/bin/env python3
"""Offline tests for failure classification and bounded patch proposal."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import diagnosis_agent as da  # noqa: E402


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.run = self.base / "run"
        (self.run / "evidence").mkdir(parents=True)
        (self.run / "evidence" / "run.json").write_text("{}\n")
        (self.run / "evidence" / "stages.tsv").write_text(
            "synth\t0\tstart\tend\nroute\t2\tstart\tend\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_classify_drt0073(self):
        log = self.run / "evidence" / "stage_5_1_grt.log"
        log.write_text("[ERROR DRT-0073] No access point for u_sram/clk\n")
        d = da.classify_failure(self.run)
        self.assertEqual(d["family"], "PIN_ACCESS")
        self.assertEqual(d["failed_stage"], "route")
        self.assertTrue(d["evidence_refs"])

    def test_classify_missing_macro_lib(self):
        log = self.run / "evidence" / "stage_synth.log"
        log.write_text("cell fakeram45_64x32 not found in library\n")
        d = da.classify_failure(self.run)
        self.assertEqual(d["family"], "MISSING_MACRO_LIB")

    def test_propose_patch_is_exact_and_pending(self):
        target = self.base / "config.mk"
        target.write_text(
            "export ADDITIONAL_LIBS = $(PLATFORM_DIR)/lib/fakeram45_64x32.lib\n"
            "export KLAYOUT_CMD ?= /usr/bin/klayout\n"
            "\n# injected failure\n"
            "export ADDITIONAL_LIBS = $(DESIGN_DIR)/lib/missing_fakeram45_64x32.lib\n")
        proposal = da.propose_patch({"family": "MISSING_MACRO_LIB"}, target)
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal["approval_status"], "PENDING")
        self.assertIn("ADDITIONAL_LIBS", proposal["patch"])
        self.assertEqual(proposal["patch_sha256"], da.sha256_text(proposal["patch"]))
        self.assertEqual(proposal["original_sha256"], da.sha256_text(target.read_text()))

    def test_no_proposal_for_unclassified_failure(self):
        target = self.base / "config.mk"
        target.write_text("x\n")
        self.assertIsNone(da.propose_patch({"family": "PIN_ACCESS"}, target))

    def test_model_absence_is_explicit(self):
        import os
        old = os.environ.pop("SATTVA_MODEL_URL", None)
        note = da.optional_model_note({"signature": "x"})
        self.assertFalse(note["available"])
        self.assertIsNone(note["note"])
        if old is not None:
            os.environ["SATTVA_MODEL_URL"] = old


if __name__ == "__main__":
    unittest.main()
