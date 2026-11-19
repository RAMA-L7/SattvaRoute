#!/usr/bin/env python3
"""Offline tests for FDE-002 exact-patch approval enforcement.

No EDA, credentials, network, hosted models, ORFS or OpenROAD are required.
All targets are temporary files; EDA binaries are stubbed where the runner is
invoked. Run: python3 -m unittest discover -s tests -p 'test_approval.py'
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sattva_approval as ap  # noqa: E402

ORIGINAL_LINE = "# original line\n"
PATCHED_LINE = "# patched line\n"


class ApprovalTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.design = self.base / "design"
        self.mirror = self.base / "mirror"
        self.scripts = self.mirror / "flow" / "scripts"
        self.state = self.base / "state"
        self.evidence = self.base / "evidence"
        self.source_run = self.base / "runs" / "source"
        for d in (self.design / "rtl", self.design / "netlist", self.design / "macro",
                  self.scripts, self.state, self.evidence,
                  self.source_run / "work" / "results" / "asap7" / "sattva_sram" / "base"):
            d.mkdir(parents=True, exist_ok=True)

        required = ["config.mk", "constraint.sdc", "pdn_sattva.tcl",
                    "rtl/sattva_ctrl.v", "rtl/sram_x4x4x1_bb.v",
                    "netlist/sattva_ctrl_synth.v", "macro/sram_x4x4x1.lef",
                    "macro/sram_x4x4x1.lib", "macro/sram_x4x4x1.gds"]
        for rel in required:
            (self.design / rel).write_text("input " + rel + "\n")

        self.target = self.scripts / "global_route.tcl"
        self.target.write_text(ORIGINAL_LINE + "keep\n")
        (self.mirror / "flow" / "Makefile").write_text("all:\n")

        self.ledger = self.state / "approval_ledger.jsonl"
        self.policy_path = self.state / "policy.json"
        self.policy = {
            "policy_id": "TEST-POLICY",
            "allowed_roots": [str(self.scripts)],
            "stages": ["check-yosys", "check-openroad", "synth", "floorplan",
                       "place", "cts", "route", "finish"],
            "stage_inputs": {"route": ["4_cts.odb"], "finish": ["5_route.odb"]},
            "input_files": required,
            "ledger": str(self.ledger),
        }
        ap.atomic_write_json(self.policy_path, self.policy)

        self.patch = self.base / "patch.diff"
        self.patch.write_text(
            "--- a/global_route.tcl\n+++ b/global_route.tcl\n"
            "@@ -1,2 +1,2 @@\n"
            f"-{ORIGINAL_LINE.rstrip(chr(10))}\n+{PATCHED_LINE.rstrip(chr(10))}\n"
            " keep\n"
        )
        (self.source_run / "work" / "results" / "asap7" / "sattva_sram" / "base" / "4_cts.odb").write_bytes(b"odb")

        self.approval = self.make_approval()
        self.approval_path = self.base / "approval.json"
        ap.atomic_write_json(self.approval_path, self.approval)

    def tearDown(self):
        self.tmp.cleanup()

    def write_approval(self, doc, path=None):
        p = path or self.approval_path
        ap.atomic_write_json(p, doc)
        return p

    def make_approval(self):
        doc = dict(
            approval_id="AP-TEST-001", decision_id="D-TEST", source_run_id="run-source-001",
            input_fingerprint=ap.compute_input_fingerprint(self.design, ap.load_policy(self.policy_path)),
            patch_sha256=ap.sha256_file(self.patch), target_file=str(self.target),
            expected_original_hash=ap.sha256_file(self.target),
            earliest_affected_stage="route", rerun_scope=["route"],
            status="APPROVED", approver="test-engineer", timestamp=ap.utc_now(),
        )
        # operation_id is derived, not stored in the approval: field mutations
        # are therefore detected as mismatches rather than masked by a stale id.
        return doc

    def validate(self, doc=None, *, for_apply=False, patch=None, run_id=None):
        return ap.validate_approval(doc or self.approval, patch or self.patch,
                                    ap.load_policy(self.policy_path), self.design,
                                    run_id=run_id or self.approval["source_run_id"],
                                    decision_id=None, for_apply=for_apply)

    def rejected(self, fn, *args, **kwargs):
        with self.assertRaises(ap.ApprovalError) as ctx:
            fn(*args, **kwargs)
        return str(ctx.exception)


class TestValidationFailures(ApprovalTestBase):
    def test_missing_approval_file(self):
        msg = self.rejected(ap.load_json, self.base / "no-such-approval.json")
        self.assertIn("invalid JSON", msg)

    def test_rejected_approval(self):
        doc = dict(self.approval, status="REJECTED")
        self.assertIn("REJECTED", self.rejected(self.validate, doc))

    def test_malformed_approval(self):
        self.approval_path.write_text("{not json")
        msg = self.rejected(ap.load_json, self.approval_path)
        self.assertIn("invalid JSON", msg)

    def test_missing_required_field(self):
        doc = dict(self.approval)
        del doc["patch_sha256"]
        self.assertIn("missing required", self.rejected(self.validate, doc))

    def test_unknown_patch(self):
        # An unrecognized patch must not satisfy an approval bound to another
        # patch, even if that patch is itself well-formed.
        other = self.base / "other.diff"
        other.write_text("--- a/x\n+++ b/x\n@@ -1 +1 @@\n-old\n+new\n")
        self.assertIn("patch SHA-256", self.rejected(self.validate, patch=other))

    def test_patch_hash_mismatch(self):
        self.patch.write_text("tampered\n")
        self.assertIn("patch SHA-256", self.rejected(self.validate))

    def test_input_fingerprint_mismatch(self):
        (self.design / "config.mk").write_text("changed input\n")
        self.assertIn("input fingerprint", self.rejected(self.validate))

    def test_run_id_mismatch(self):
        self.assertIn("run id mismatch", self.rejected(self.validate, run_id="other-run"))

    def test_decision_id_mismatch(self):
        with self.assertRaises(ap.ApprovalError):
            ap.validate_approval(self.approval, self.patch, ap.load_policy(self.policy_path),
                                 self.design, run_id=self.approval["source_run_id"],
                                 decision_id="D-OTHER")

    def test_rerun_scope_mismatch(self):
        doc = dict(self.approval, rerun_scope=["place", "route"])
        self.assertIn("contiguous", self.rejected(self.validate, doc))

    def test_target_original_hash_mismatch(self):
        self.target.write_text("concurrent change\n")
        self.assertIn("original hash", self.rejected(self.validate))

    def test_invalid_target_path_relative(self):
        doc = dict(self.approval, target_file="relative/global_route.tcl")
        self.assertIn("must be absolute", self.rejected(self.validate, doc))

    def test_path_traversal(self):
        doc = dict(self.approval, target_file=str(self.scripts / ".." / "escape.tcl"))
        self.assertIn("traversal", self.rejected(self.validate, doc))

    def test_symlink_escape(self):
        outside = self.base / "outside"
        outside.mkdir()
        link = self.scripts / "escape"
        link.symlink_to(outside, target_is_directory=True)
        doc = dict(self.approval, target_file=str(link / "global_route.tcl"))
        self.assertIn("symlink", self.rejected(self.validate, doc))

    def test_target_outside_boundary(self):
        outside = self.base / "outside.tcl"
        outside.write_text(ORIGINAL_LINE)
        doc = dict(self.approval, target_file=str(outside),
                   expected_original_hash=ap.sha256_file(outside))
        self.assertIn("outside permitted boundary", self.rejected(self.validate, doc))

    def test_operation_id_tamper(self):
        doc = dict(self.approval, operation_id="0" * 64)
        self.assertIn("operation_id", self.rejected(self.validate, doc))


class TestApplication(ApprovalTestBase):
    def apply(self, doc=None):
        policy = ap.load_policy(self.policy_path)
        policy["_design_root"] = str(self.design)
        return ap.apply_patch(doc or self.approval, self.patch, policy, self.evidence)

    def test_atomic_application_and_post_verify(self):
        record = self.apply()
        self.assertEqual(record["phase"], "verified")
        self.assertEqual(self.target.read_text(), ORIGINAL_LINE.replace("original", "patched") + "keep\n")
        state = ap.load_json(self.evidence / "approval_apply.json")
        self.assertEqual(state["phase"], "verified")
        self.assertEqual(state["before_sha256"], self.approval["expected_original_hash"])
        self.assertEqual(state["after_sha256"], ap.sha256_file(self.target))
        backup = Path(record["backup"])
        self.assertTrue(backup.exists())
        self.assertEqual(backup.read_text(), ORIGINAL_LINE + "keep\n")

    def test_post_apply_verification_failure_rolls_back(self):
        original = ap.sha256_file
        def fake(path):
            p = Path(path)
            if p == self.target and b"patched line" in p.read_bytes():
                return "0" * 64
            return original(path)
        with mock.patch.object(ap, "sha256_file", fake):
            self.assertIn("post-apply", self.rejected(self.apply))
        self.assertEqual(self.target.read_text(), ORIGINAL_LINE + "keep\n")
        state = ap.load_json(self.evidence / "approval_apply.json")
        self.assertEqual(state["phase"], "rolled_back")

    def test_concurrent_target_modification_rejected(self):
        lock = self.scripts / ".global_route.tcl.sattva.lock"
        lock.write_text(str(os.getpid()))
        self.assertIn("another application", self.rejected(self.apply))
        lock.unlink()
        self.assertEqual(self.target.read_text(), ORIGINAL_LINE + "keep\n")

    def test_approval_reuse_rejected(self):
        self.apply()
        self.assertIn("reuse", self.rejected(self.apply))

    def test_restart_recovery_resumes_completed_apply(self):
        policy = ap.load_policy(self.policy_path)
        policy["_design_root"] = str(self.design)
        args = type("Args", (), dict(
            policy=str(self.policy_path), design_root=str(self.design),
            approval=str(self.approval_path), patch=str(self.patch),
            evidence_dir=str(self.evidence), run_id=self.approval["source_run_id"],
            decision_id=None))()
        self.apply()
        ap.cmd_guard(args)
        guard = ap.load_json(self.evidence / "approval_guard.json")
        self.assertEqual(guard["apply_phase"], "resumed")
        self.assertEqual(guard["status"], "PASS")

    def test_interrupted_apply_state_is_refused(self):
        ap.atomic_write_json(self.evidence / "approval_apply.json", dict(
            operation_id=ap.operation_id(self.approval), phase="started"))
        msg = self.rejected(self.apply)
        self.assertIn("interrupted", msg)


class TestRunnerBoundary(ApprovalTestBase):
    def setUp(self):
        super().setUp()
        self.bin = self.base / "bin"
        self.bin.mkdir()
        for name, body in (
            ("make", "#!/bin/bash\nif [ \"${1:-}\" = '-v' ]; then echo 'GNU Make stub'; exit 0; fi\nexit \"${STUB_RC:-0}\"\n"),
            ("openroad", "#!/bin/bash\necho 'OpenROAD stub'\n"),
            ("yosys", "#!/bin/bash\necho 'Yosys stub'\n"),
        ):
            p = self.bin / name
            p.write_text(body)
            p.chmod(0o755)

    def run_runner(self, approval_path=None, decision="D-TEST"):
        env = os.environ.copy()
        env.update(PATH=f"{self.bin}:{env['PATH']}", SATTVA_ROOT=str(self.base),
                   SATTVA_MIRROR=str(self.mirror), SATTVA_DESIGN=str(self.design),
                   SATTVA_RUNS=str(self.base / "runs-out"),
                   OPENROAD_EXE=str(self.bin / "openroad"),
                   YOSYS_EXE=str(self.bin / "yosys"),
                   SATTVA_APPROVAL=str(approval_path or self.approval_path),
                   SATTVA_PATCH=str(self.patch), SATTVA_POLICY=str(self.policy_path),
                   SATTVA_SOURCE_RUN=str(self.source_run),
                   SATTVA_SOURCE_RUN_ID=self.approval["source_run_id"],
                   SATTVA_DECISION_ID=decision, STUB_RC="0")
        import subprocess
        proc = subprocess.run(["bash", str(ROOT / "scripts" / "run_baseline_orfs.sh")],
                              env=env, capture_output=True, text=True, timeout=120)
        runs = sorted((self.base / "runs-out").glob("orfs_baseline_*"))
        return proc, (runs[-1] if runs else None)

    def test_valid_approval_runs_only_declared_scope(self):
        proc, run = self.run_runner()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((run / "evidence" / "approval_guard.json").exists())
        self.assertEqual((run / "evidence" / "stages.tsv").read_text().strip().split("\t")[0], "route")
        self.assertEqual(len((run / "evidence" / "stages.tsv").read_text().splitlines()), 1)
        self.assertIn("patched line", self.target.read_text())

    def test_invalid_approval_blocks_execution_boundary(self):
        self.patch.write_text("tampered patch\n")
        proc, run = self.run_runner()
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("APPROVAL_ERROR", proc.stderr)
        self.assertFalse((run / "evidence" / "stages.tsv").exists())
        self.assertEqual(self.target.read_text(), ORIGINAL_LINE + "keep\n")

    def test_scope_needs_evidence_based_source_artifacts(self):
        artifact = self.source_run / "work" / "results" / "asap7" / "sattva_sram" / "base" / "4_cts.odb"
        artifact.unlink()
        self.approval["rerun_scope"] = ["route"]
        self.write_approval(self.approval)
        proc, run = self.run_runner()
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("source artifacts missing", proc.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
