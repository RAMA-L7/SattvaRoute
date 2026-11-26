#!/usr/bin/env python3
"""Fixtures for the profile-scoped dependency manifest (offline, no EDA)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import manifest as M  # noqa: E402


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.mirror = self.root / "mirror"
        self.design = self.root / "benchmark" / "design" / "control"
        self.platform = self.mirror / "flow" / "platforms" / "fake"
        self.tools = self.root / "tools"
        for d in (self.design / "rtl", self.design / "netlist",
                  self.platform / "lib", self.platform / "lef",
                  self.mirror / "flow" / "scripts", self.tools):
            d.mkdir(parents=True, exist_ok=True)
        self._write_tree()
        self.manifest = self.root / "manifest.json"
        self._write_manifest()

    def tearDown(self):
        self.tmp.cleanup()

    # ------------------------------------------------------------------
    def _write_tree(self):
        files = {
            self.design / "config.mk": "export PLATFORM=fake\n",
            self.design / "constraint.sdc": "create_clock -period 1\n",
            self.design / "rtl" / "top.v": "module top; endmodule\n",
            self.design / "rtl" / "macro_bb.v": "module macro; endmodule\n",
            self.design / "netlist" / "top_synth.v": "module top; endmodule\n",
            self.design / "netlist" / "provenance.txt": "prepared\n",
            self.platform / "lib" / "sc.lib": "time_unit : 1ns;\n",
            self.platform / "lib" / "macro.lib": "cell(macro) {}\n",
            self.platform / "lef" / "tech.lef": "VERSION 1 ;\n",
            self.platform / "lef" / "macro.lef": "MACRO macro ;\n",
            self.platform / "rcx.rules": "Extraction Rules\n",
            self.platform / "setRC.tcl": "set_wire_rc -layer metal1\n",
            self.mirror / "flow" / "Makefile": "all:\n",
            self.mirror / "flow" / "scripts" / "route.tcl": "# route\n",
            self.tools / "openroad": "openroad-binary\n",
            self.tools / "yosys": "yosys-binary\n",
        }
        for path, text in files.items():
            path.write_text(text, encoding="utf-8")
        # platform hashes are declared from the actual files
        self.platform_hashes = {
            str(p.relative_to(self.platform)): M.sha256_file(p)
            for p in self.platform.rglob("*") if p.is_file()
        }

    def _write_manifest(self, *, inactive_missing=True, tool_hash=None,
                        revision="deadbeef", verify=True):
        prof = {
            "description": "synthetic active profile",
            "design_root": str(self.design.relative_to(self.root)).replace("\\", "/"),
            "platform_dir": str(self.platform.relative_to(self.mirror)).replace("\\", "/"),
            "design_files": ["config.mk", "constraint.sdc", "rtl/top.v",
                             "rtl/macro_bb.v", "netlist/top_synth.v",
                             "netlist/provenance.txt"],
            "approval_inputs": ["config.mk", "constraint.sdc",
                                "netlist/top_synth.v"],
            "platform_files": self.platform_hashes,
            "flow_files": ["flow/Makefile", "flow/scripts/route.tcl"],
        }
        inactive = {
            "description": "inactive profile with deliberately absent files",
            "design_root": "benchmark/design/absent",
            "platform_dir": "flow/platforms/absent",
            "design_files": ["config.mk", "does_not_exist.v"] if inactive_missing else [],
            "approval_inputs": [],
            "platform_files": {},
            "flow_files": [],
        }
        doc = {
            "manifest_id": "TEST-MANIFEST",
            "version": 2,
            "orfs": {"revision": revision, "root_default": "mirror",
                     "verify_revision": verify, "local_patches": []},
            "tools": {
                "openroad": {"default": str(self.tools / "openroad"),
                             "expected_sha256": tool_hash or M.sha256_file(self.tools / "openroad")},
                "yosys": {"default": str(self.tools / "yosys"),
                          "expected_sha256": M.sha256_file(self.tools / "yosys")},
            },
            "profiles": {"active": prof, "inactive": inactive},
        }
        self.manifest.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    def check(self, **kw):
        return M.check(self.manifest, self.root, "active", use_git=False, **kw)

    # ------------------------------------------------------------------
    def test_clean_profile_passes(self):
        out = self.check()
        self.assertEqual(out["status"], M.PASS, out)
        self.assertFalse(out["missing"])
        self.assertFalse(out["mismatches"])
        self.assertEqual(out["inactive_profiles"], ["inactive"])

    def test_inactive_profile_never_blocks_active(self):
        out = self.check()
        self.assertEqual(out["status"], M.PASS)
        names = {c["name"] for c in out["checks"]}
        self.assertFalse(any("does_not_exist" in n for n in names))

    def test_macro_model_change_invalidates_fingerprint_and_fails(self):
        before = self.check()["fingerprint"]
        (self.platform / "lib" / "macro.lib").write_text("cell(macro) { changed }\n",
                                                         encoding="utf-8")
        after = self.check()
        self.assertEqual(after["status"], M.FAIL)
        self.assertNotEqual(before, after["fingerprint"])
        self.assertTrue(any(m["kind"] == "platform" for m in after["mismatches"]))

    def test_sdc_change_invalidates_fingerprint(self):
        before = self.check()["fingerprint"]
        (self.design / "constraint.sdc").write_text(
            "create_clock -period 1000\n", encoding="utf-8")
        after = self.check()
        self.assertNotEqual(before, after["fingerprint"])

    def test_placement_or_flow_change_invalidates_fingerprint(self):
        before = self.check()["fingerprint"]
        (self.mirror / "flow" / "scripts" / "route.tcl").write_text(
            "# changed\n", encoding="utf-8")
        after = self.check()
        self.assertNotEqual(before, after["fingerprint"])

    def test_extraction_rule_change_fails(self):
        (self.platform / "rcx.rules").write_text("changed rules\n", encoding="utf-8")
        out = self.check()
        self.assertEqual(out["status"], M.FAIL)
        self.assertTrue(any("rcx.rules" in m["name"] for m in out["mismatches"]))

    def test_tool_identity_mismatch_fails(self):
        self._write_manifest(tool_hash="0" * 64)
        out = self.check()
        self.assertEqual(out["status"], M.FAIL)
        self.assertTrue(any(m["kind"] == "tool" for m in out["mismatches"]))

    def test_tool_identity_matches_executed_binary(self):
        out = self.check()
        self.assertEqual(out["status"], M.PASS)
        self.assertEqual(out["captured"]["tools"]["openroad"],
                         M.sha256_file(self.tools / "openroad"))

    def test_missing_required_file_fails(self):
        (self.design / "netlist" / "top_synth.v").unlink()
        out = self.check()
        self.assertEqual(out["status"], M.FAIL)
        self.assertTrue(any("top_synth.v" in m for m in out["missing"]))

    # ---- git-backed checks -------------------------------------------
    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_revision_mismatch_fails(self):
        subprocess.run(["git", "init", "-q", str(self.mirror)], check=True)
        subprocess.run(["git", "-C", str(self.mirror), "config",
                        "user.email", "t@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.mirror), "config",
                        "user.name", "t"], check=True)
        subprocess.run(["git", "-C", str(self.mirror), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.mirror), "commit", "-qm", "init"],
                       check=True)
        head = subprocess.run(["git", "-C", str(self.mirror), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
        self._write_manifest(revision=head)
        ok = M.check(self.manifest, self.root, "active")
        self.assertEqual(ok["status"], M.PASS, ok)
        self._write_manifest(revision="0" * 40)
        bad = M.check(self.manifest, self.root, "active")
        self.assertEqual(bad["status"], M.FAIL)
        self.assertTrue(any(m["kind"] == "orfs_revision" for m in bad["mismatches"]))

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_unexpected_tracked_change_fails(self):
        subprocess.run(["git", "init", "-q", str(self.mirror)], check=True)
        subprocess.run(["git", "-C", str(self.mirror), "config",
                        "user.email", "t@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.mirror), "config",
                        "user.name", "t"], check=True)
        subprocess.run(["git", "-C", str(self.mirror), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.mirror), "commit", "-qm", "init"],
                       check=True)
        head = subprocess.run(["git", "-C", str(self.mirror), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
        self._write_manifest(revision=head)
        (self.mirror / "flow" / "scripts" / "route.tcl").write_text(
            "# undeclared local edit\n", encoding="utf-8")
        out = M.check(self.manifest, self.root, "active")
        self.assertEqual(out["status"], M.FAIL)
        self.assertTrue(any(m["kind"] == "orfs_unexpected_changes"
                            for m in out["mismatches"]))

    def test_no_git_skips_revision(self):
        out = M.check(self.manifest, self.root, "active", use_git=False)
        self.assertEqual(out["status"], M.PASS)
        self.assertEqual(out["captured"]["orfs_revision"], None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
