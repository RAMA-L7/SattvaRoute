#!/usr/bin/env python3
"""Offline tests for the SattvaRoute incremental Knowledge Base.

No EDA, network, hosted model, ORFS or OpenROAD required. All writes go to
temporary directories. Covers the 20 required KB test scenarios.
Run: python3 -m unittest discover -s tests -p 'test_kb.py' -v
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sattva_kb as kb  # noqa: E402


class KBCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.kb_root = self.base / "knowledge"
        self.kb_root.mkdir()
        self.store_path = self.kb_root / "kb_records.jsonl"
        self.store = kb.KBStore(self.store_path, self.kb_root)

    def tearDown(self):
        self.tmp.cleanup()

    def make_record(self, kid, **over):
        rec = {
            "knowledge_id": kid, "record_version": 1, "created_at": kb.utc_now(),
            "identity": {"investigation_id": "FDE-TEST", "fde_id": "FDE-TEST",
                         "experiment_ids": [], "design_id": "sattva_sram",
                         "design_fingerprint": "DESIGN-A", "source_run": "run-1",
                         "timestamp": kb.utc_now()},
            "failure": {"category": "pin_access",
                        "signature": "DRT-0073 No access point for u_sram/clk",
                        "violation_type": "DRT-0073", "tool": "openroad",
                        "tool_version": "bazel-nostamp", "technology": "asap7",
                        "geometry": "M4 thin clk pin", "routing_layers": ["M4", "M5"],
                        "constraints": "default", "environment": "WSL", "pvt": None,
                        "logs": ["logs/5_1_grt.log"], "reports": ["docs/FDE-TEST.md"],
                        "metrics": {"accepted_ap": 3}},
            "root_cause": {"status": "ESTABLISHED",
                           "hypothesis": "M4 OBS blocks planar escape of clk pin",
                           "supporting_evidence": ["same-binary A/B"],
                           "contradicting_evidence": [], "confidence": "HIGH",
                           "alternative_explanations": [], "unresolved_questions": []},
            "remedies": [{"remedy_id": "R-A", "remedy_family": "M4_OBS_CORRIDOR",
                          "description": "narrow M4 OBS corridor",
                          "exact_modifications": "OBS x3534-3672",
                          "preconditions": ["GDS empty strip"], "compatibility": {},
                          "expected_outcome": "AP accepted", "risks": ["exposes metal"],
                          "side_effects": ["spacing markers"], "outcome": "PASS"}],
            "experiment": {"experiment_id": "EXP-" + kid, "baseline_reference": "run-1",
                           "scratch_environment": "experiments/FDE-007/.../scratch_design",
                           "exact_changes": "M4 OBS only", "tool_invocation": "pin_access",
                           "configuration": "cfg", "execution_status": "EXECUTED",
                           "reproducibility": "run id", "estimated_cost": "diagnostic"},
            "outcome": {"state": "PASS", "summary": "resolved"},
            "applicability": {"scope": "DESIGN_SPECIFIC",
                              "conditions": ["asap7", "m4 pin", "narrow strip free"],
                              "validated_characteristics": ["sram_x4x4x1"],
                              "limitations": ["scratch only"], "exclusions": [],
                              "compatible_environments": ["asap7/openroad"],
                              "cross_design_reuse": "conditional"},
            "evidence": {"observations": ["o1", "o2"], "hypotheses": ["h1"],
                         "inferences": ["i1"], "experimentally_supported": ["3 accepted APs"],
                         "validated_knowledge": ["OBS blocks planar escape"],
                         "checksums": {"lef": "abc"}, "before_after": "0 to 3 APs",
                         "reviewer_findings": ["R-011"]},
            "relationships": {"related_ids": [], "duplicate_of": None,
                              "supersedes": None, "remedy_family": "M4_OBS_CORRIDOR"},
            "maturity": 2,
            "provenance": {"fde_records": ["docs/FDE-TEST.md"], "source_hashes": {},
                           "record_source": "unit-test"},
        }
        for k, v in over.items():
            if k in rec and isinstance(rec[k], dict) and isinstance(v, dict):
                rec[k].update(v)
            else:
                rec[k] = v
        return rec

    def query(self, **over):
        q = {"failure_signature": "DRT-0073 No access point for u_sram/clk",
             "violation_type": "DRT-0073",
             "root_cause_hypothesis": "M4 OBS blocks planar escape of clk pin",
             "technology": "asap7", "routing_layers": ["M4", "M5"], "tool": "openroad",
             "design_fingerprint": "DESIGN-A",
             "context_terms": ["asap7", "m4 pin", "narrow strip free"],
             "required_validation": ["controlled validation in scratch"],
             "exact_modifications": "OBS x3534-3672"}
        q.update(over)
        return q

    def add(self, kid, **over):
        return self.store.append(self.make_record(kid, **over))


class TestKnowledgeLifecycle(KBCase):
    def test_01_empty_kb(self):
        self.assertEqual(kb.metrics(self.store)["total_records"], 0)
        res = kb.assess(self.store, self.query())
        self.assertEqual(res["classification"], "NO_RELEVANT_KNOWLEDGE")
        self.assertEqual(kb.search(self.store, self.query())["total_matches"], 0)

    def test_02_applicable_remedy_strong_match(self):
        self.add("KB-0001")
        res = kb.assess(self.store, self.query())
        self.assertEqual(res["classification"], "STRONG_MATCH")
        self.assertEqual(res["recommendation"]["knowledge_id"], "KB-0001")
        self.assertTrue(res["recommendation"]["record_sha256"])
        self.assertTrue(res["recommendation"]["required_validation"])

    def test_03_incompatible_conditions(self):
        self.add("KB-0001", applicability={"exclusions": ["m4 pin"]})
        res = kb.assess(self.store, self.query())
        self.assertEqual(res["classification"], "INCOMPATIBLE")

    def test_04_previously_failed_remedy_searchable(self):
        self.add("KB-0001", outcome={"state": "FAIL", "summary": "no APs"})
        found = kb.search(self.store, self.query())
        self.assertEqual(found["total_matches"], 1)
        self.assertEqual(found["results"][0]["outcome"], "FAIL")
        res = kb.assess(self.store, self.query())
        self.assertEqual(res["classification"], "PREVIOUSLY_FAILED")

    def test_05_new_investigation_no_solution(self):
        self.add("KB-0001")
        res = kb.assess(self.store, self.query(
            failure_signature="PDN-0006 missing power stripe", violation_type="PDN-0006",
            context_terms=["power", "stripe"]))
        self.assertEqual(res["classification"], "NO_RELEVANT_KNOWLEDGE")

    def test_06_success_capture(self):
        sealed = self.add("KB-0001")
        self.assertEqual(sealed["integrity"]["algorithm"], "sha256")
        self.assertEqual(kb.metrics(self.store)["by_outcome"]["PASS"], 1)
        self.assertEqual(kb.metrics(self.store)["maturity_histogram"]["2"], 1)

    def test_07_failed_experiment_negative_knowledge(self):
        self.add("KB-0001", outcome={"state": "FAIL", "summary": "0 APs"},
                 maturity=1, evidence={"validated_knowledge": [],
                                       "experimentally_supported": ["0 accepted APs"]})
        m = kb.metrics(self.store)
        self.assertEqual(m["by_outcome"]["FAIL"], 1)
        rec = self.store.load()[0]
        self.assertNotIn("PASS", rec["outcome"]["state"])

    def test_08_inconclusive_not_validation(self):
        self.add("KB-0001", outcome={"state": "INCONCLUSIVE", "summary": "2 nm sliver"},
                 maturity=1)
        res = kb.assess(self.store, self.query())
        self.assertNotIn(res["classification"], ("STRONG_MATCH",))
        with self.assertRaises(kb.KBError):
            self.store.append(self.make_record("KB-0002", outcome={"state": "INCONCLUSIVE"},
                                               maturity=3))

    def test_09_cross_design_compatibility_aware(self):
        self.add("KB-0001")
        res = kb.assess(self.store, self.query(design_fingerprint="DESIGN-B"))
        self.assertEqual(res["classification"], "PARTIAL_MATCH")
        self.assertIn("cross-design", res["reason"].lower())

    def test_10_duplicate_knowledge_detection(self):
        self.add("KB-0001")
        duplicate = self.make_record("KB-0002")  # identical content, new proposed ID
        dup = kb.duplicate_check(duplicate, self.store)
        self.assertTrue(any(m["kind"] == "exact_duplicate" for m in dup["matches"]))

    def test_11_duplicate_experiment_suppression(self):
        # FDE-007 R1-N and R1-N-W are ONE family, parameter variants, both FAIL.
        self.add("KB-R1N", outcome={"state": "FAIL", "summary": "DRT-0073"},
                 maturity=1,
                 evidence={"validated_knowledge": [],
                           "experimentally_supported": ["0 accepted APs"]})
        variant = self.make_record("KB-R1NW", outcome={"state": "FAIL", "summary": "DRT-0073"},
                                   maturity=1,
                                   evidence={"validated_knowledge": [],
                                             "experimentally_supported": ["0 accepted APs"]})
        variant["remedies"][0]["exact_modifications"] = "OBS x3474-3672"
        variant["relationships"]["related_ids"] = ["KB-R1N"]
        dup = kb.duplicate_check(variant, self.store)
        kinds = {m["kind"] for m in dup["matches"]}
        self.assertIn("parameter_variation", kinds)
        self.assertNotIn("exact_duplicate", kinds)
        self.assertTrue(all(m["family"] == "M4_OBS_CORRIDOR" for m in dup["matches"]))
        res = kb.assess(self.store, self.query(failure_signature="DRT-0073 clk",
                                               exact_modifications="OBS x3474-3672"))
        self.assertEqual(res["classification"], "PREVIOUSLY_FAILED")

    def test_12_provenance_verification(self):
        sealed = self.add("KB-0001")
        self.assertEqual(self.store.verify()["status"], "PASS")
        tampered = json.loads(json.dumps(sealed))
        tampered["failure"]["signature"] = "TAMPERED"
        self.store_path.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
        self.assertEqual(self.store.verify()["status"], "FAIL")

    def test_13_append_only_history(self):
        self.add("KB-0001")
        before = self.store_path.read_bytes()
        self.add("KB-0002")
        after = self.store_path.read_bytes()
        self.assertTrue(after.startswith(before))
        self.assertEqual(len(self.store.load()), 2)
        with self.assertRaises(kb.KBError):
            self.store.append(self.make_record("KB-0001"))

    def test_14_production_artifact_protection(self):
        with self.assertRaises(kb.KBError):
            kb.assert_safe_write(self.base / "runs" / "evil.jsonl", self.kb_root)
        with self.assertRaises(kb.KBError):
            kb.assert_safe_write(self.kb_root.parent / "benchmark" / "evil", self.kb_root)
        # KB itself is writable.
        kb.assert_safe_write(self.kb_root / "ok.jsonl", self.kb_root)

    def test_15_baseline_immutability(self):
        proj = self.base / "project"
        (proj / "state").mkdir(parents=True)
        (proj / "benchmark").mkdir()
        protected = proj / "benchmark" / "design.lef"
        protected.write_text("original", encoding="utf-8")
        manifest = self.kb_root / "kb_immutable_manifest.json"
        kb.atomic_write_json(manifest, {"protected_hashes": {"benchmark/design.lef":
                                                              kb.sha256_file(protected)}})
        self.assertEqual(kb.check_immutable(manifest, proj)["status"], "PASS")
        protected.write_text("modified", encoding="utf-8")
        check = kb.check_immutable(manifest, proj)
        self.assertEqual(check["status"], "FAIL")
        self.assertIn("benchmark/design.lef", check["changed"])

    def test_16_scratch_isolation(self):
        rec = self.make_record("KB-0001")
        rec["experiment"]["scratch_environment"] = "benchmark/design/sattva_sram"
        with self.assertRaises(kb.KBError):
            self.store.append(rec)

    def test_17_retrieval_after_new_record(self):
        self.assertEqual(kb.search(self.store, self.query())["total_matches"], 0)
        self.add("KB-0001")
        self.assertEqual(kb.search(self.store, self.query())["total_matches"], 1)

    def test_18_contradictory_findings_preserved(self):
        self.add("KB-PASS", outcome={"state": "PASS", "summary": "worked"})
        self.add("KB-FAIL", outcome={"state": "FAIL", "summary": "failed"},
                 maturity=1,
                 evidence={"validated_knowledge": [],
                           "experimentally_supported": ["0 accepted APs"]})
        self.assertEqual(len(self.store.load()), 2)
        outcomes = {r["outcome"] for r in kb.search(self.store, self.query())["results"]}
        self.assertEqual(outcomes, {"PASS", "FAIL"})

    def test_19_reconsideration_with_new_evidence(self):
        self.add("KB-0001", outcome={"state": "FAIL", "summary": "0 APs"},
                 maturity=1,
                 evidence={"validated_knowledge": [],
                           "experimentally_supported": ["0 accepted APs"]})
        res = kb.assess(self.store, self.query(
            new_justification="new GDS provenance at sliver",
            new_evidence_refs=["experiments/FDE-007/sliver_gds_census.json"]))
        self.assertEqual(res["classification"], "PARTIAL_MATCH")
        self.assertNotEqual(res["classification"], "STRONG_MATCH")
        # Free-form justification without evidence references cannot bypass suppression.
        blocked = kb.assess(self.store, self.query(new_justification="trust me, it is different"))
        self.assertEqual(blocked["classification"], "PREVIOUSLY_FAILED")
        self.assertEqual(blocked["distinct_families"], 1)

    def test_20_unsupported_success_claim_rejected(self):
        rec = self.make_record("KB-0001", evidence={"experimentally_supported": [],
                                                    "validated_knowledge": [],
                                                    "checksums": {}})
        with self.assertRaises(kb.KBError):
            self.store.append(rec)


    def test_21_diagnostic_pass_is_not_a_remedy(self):
        rec = self.make_record("KB-DIAG")
        rec["relationships"]["remedy_family"] = "CANDIDATE_DIAGNOSTIC"
        rec["remedies"][0]["remedy_family"] = "CANDIDATE_DIAGNOSTIC"
        self.store.append(rec)
        res = kb.assess(self.store, self.query(
            failure_signature="DRT-0073", violation_type="DRT-0073",
            root_cause_hypothesis="M4 OBS blocks planar escape of clk pin"))
        self.assertNotEqual(res["classification"], "STRONG_MATCH")


if __name__ == "__main__":
    unittest.main()
