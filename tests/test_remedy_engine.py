#!/usr/bin/env python3
"""Offline unit tests for the remedy-first workflow engine. No EDA required."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import remedy_engine as re_  # noqa: E402


def cand(cid, family="F", **over):
    base = dict(candidate_id=cid, family=family, mechanism="m",
                evidence_strength="SOURCE_VERIFIED", applicability="EXACT",
                effectiveness=0.8, risk=0.2, cost_minutes=30,
                reversibility="FULL", sources=["https://example.test"],
                legality="PASS", predicted_outcome="AP accepted")
    base.update(over)
    return re_.Candidate(**base)


class RankingTests(unittest.TestCase):
    def setUp(self):
        self.budgets = re_.load_budgets()

    def test_deterministic_descending_order(self):
        cs = [cand("A", effectiveness=0.4), cand("B", effectiveness=0.9)]
        r1 = re_.rank_candidates(cs, [], self.budgets)
        r2 = re_.rank_candidates(list(reversed(cs)), [], self.budgets)
        self.assertEqual([x.candidate_id for x in r1], ["B", "A"])
        self.assertEqual([x.candidate_id for x in r1],
                         [x.candidate_id for x in r2])
        self.assertGreater(r1[0].score, r1[1].score)

    def test_refuted_family_auto_eliminated(self):
        cs = [cand("A", family="HAND_CARVE"), cand("B", family="GENERATOR")]
        ranked = re_.rank_candidates(cs, ["HAND_CARVE"], self.budgets)
        self.assertFalse(next(r for r in ranked if r.candidate_id == "A").eligible)
        self.assertTrue(next(r for r in ranked if r.candidate_id == "B").eligible)

    def test_incompatible_and_illegal_eliminated(self):
        cs = [cand("A", applicability="INCOMPATIBLE"), cand("B", legality="FAIL")]
        ranked = re_.rank_candidates(cs, [], self.budgets)
        self.assertTrue(all(not r.eligible for r in ranked))

    def test_score_components_traceable(self):
        ranked = re_.rank_candidates([cand("A")], [], self.budgets)
        self.assertEqual(set(ranked[0].components),
                         set(self.budgets["weights"]))


class KBRefutationTests(unittest.TestCase):
    def test_extract_refuted_from_kb_schema(self):
        import json
        import tempfile
        rec = {
            "knowledge_id": "KB-X", "record_version": 1, "created_at": "2026-01-01T00:00:00+00:00",
            "identity": {"investigation_id": "X", "fde_id": "X", "design_id": "d",
                         "design_fingerprint": "f", "source_run": "r"},
            "failure": {"category": "pin_access",
                        "signature": "DRT-0073 No access point for u_sram/clk",
                        "violation_type": "DRT-0073", "tool": "openroad",
                        "technology": "asap7"},
            "root_cause": {"status": "ESTABLISHED", "hypothesis": "h"},
            "remedies": [{"remedy_id": "R1", "remedy_family": "HAND_CARVE",
                          "description": "x carve", "outcome": "FAIL"}],
            "experiment": {"experiment_id": "E1", "execution_status": "RUN"},
            "outcome": {"state": "FAIL"},
            "applicability": {"scope": "REUSABLE", "conditions": [], "exclusions": []},
            "evidence": {"observations": [], "inferences": [],
                         "experimentally_supported": [], "validated_knowledge": [],
                         "checksums": {}, "reviewer_findings": []},
            "relationships": {"related_ids": [], "remedy_family": "HAND_CARVE"},
            "maturity": 1,
            "provenance": {"fde_records": [], "source_hashes": {}},
        }
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "kb.jsonl"
            p.write_text(json.dumps(rec) + "\n", encoding="utf-8")
            self.assertIn("HAND_CARVE", re_.kb_refuted_families(p, "DRT-0073"))
            self.assertEqual(re_.kb_refuted_families(p, "OTHER-SIG"), [])


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.budgets = re_.load_budgets()
        self.clock = [0.0]
        self.now = lambda: self.clock[0]

    def test_full_demo_stage_sequence_and_no_implicit_execution(self):
        eng = re_.RemedyEngine("DRT-0073", self.budgets, now_fn=self.now)
        eng.diagnose({"signature": "DRT-0073", "source": "ENG013"})
        eng.research([cand("C1")], {"C1": ["https://example.test"]}, ["HAND_CARVE"])
        selected = eng.rank_and_select()
        self.assertIsNotNone(selected)
        eng.sandbox_and_validate(selected)
        out = eng.report()
        self.assertEqual(out["execution_state"], "NOT_RUN")
        self.assertEqual(out["stages"],
                         ["FAILURE", "DIAGNOSIS", "RESEARCH", "RANK", "SELECT",
                          "SANDBOX", "VALIDATE", "REPORT"])

    def test_failed_attempt_advances_to_next_candidate(self):
        eng = re_.RemedyEngine("X", self.budgets, now_fn=self.now)
        eng.diagnose({"signature": "X"})
        eng.research([cand("A", effectiveness=0.9), cand("B", effectiveness=0.5)],
                     {}, [])
        first = eng.rank_and_select()
        self.assertEqual(first.candidate_id, "A")
        second = eng.record_failure_and_advance("A", "0 APs")
        self.assertIsNotNone(second)
        self.assertEqual(second.candidate_id, "B")
        self.assertEqual(eng.result.evidence["attempts"][0]["outcome"], "FAIL")

    def test_illegal_candidate_sets_risk_stop(self):
        eng = re_.RemedyEngine("X", self.budgets, now_fn=self.now)
        eng.diagnose({"signature": "X"})
        eng.research([cand("A", legality="FAIL")], {}, [])
        self.assertIsNone(eng.rank_and_select())
        self.assertEqual(eng.report()["stop_condition"], "RISK_EXCEEDS_POLICY")

    def test_budget_expiry_produces_unresolved_not_fix(self):
        budgets = dict(self.budgets)
        budgets["budgets_minutes"] = dict(self.budgets["budgets_minutes"])
        budgets["budgets_minutes"]["COMMON_ISSUE_TOTAL"] = 0
        clock = [1000.0]
        eng = re_.RemedyEngine("X", budgets, now_fn=lambda: clock[0])
        eng.diagnose({"signature": "X"})
        clock[0] += 10000.0  # simulate elapsed time within the stage
        out = eng.report()
        self.assertEqual(out["stop_condition"], "TIME_BUDGET_EXPIRED")
        self.assertIn("time budget expired", out["unresolved_gap"])
        self.assertNotEqual(out["execution_state"], "PASS")

    def test_verified_pass_emits_fix_verified(self):
        eng = re_.RemedyEngine("X", self.budgets, now_fn=self.now,
                               execute=lambda c: {"state": "PASS", "verified": True,
                                                  "independent_review": "PASS"},
                               authorized=True)
        eng.diagnose({"signature": "X"})
        eng.research([cand("A")], {}, [])
        eng.sandbox_and_validate(eng.rank_and_select())
        self.assertEqual(eng.report()["stop_condition"], "FIX_VERIFIED")

    def test_pass_without_evidence_is_not_a_fix(self):
        eng = re_.RemedyEngine("X", self.budgets, now_fn=self.now,
                               execute=lambda c: {"state": "PASS"}, authorized=True)
        eng.diagnose({"signature": "X"})
        eng.research([cand("A")], {}, [])
        eng.sandbox_and_validate(eng.rank_and_select())
        out = eng.report()
        self.assertEqual(out["stop_condition"], "UNVERIFIED_PASS")
        self.assertNotEqual(out["execution_state"], "NOT_RUN")

    def test_timeout_neutralises_pass(self):
        clock = [0.0]
        def execute(c):
            clock[0] += 10000.0
            return {"state": "PASS", "verified": True,
                    "independent_review": "PASS"}
        budgets = dict(self.budgets)
        budgets["budgets_minutes"] = dict(self.budgets["budgets_minutes"])
        budgets["budgets_minutes"]["VALIDATE"] = 0
        eng = re_.RemedyEngine("X", budgets, now_fn=lambda: clock[0],
                               execute=execute, authorized=True)
        eng.diagnose({"signature": "X"})
        eng.research([cand("A")], {}, [])
        eng.sandbox_and_validate(eng.rank_and_select())
        out = eng.report()
        self.assertEqual(out["stop_condition"], "TIME_BUDGET_EXPIRED")
        self.assertEqual(out["execution_state"], "INCONCLUSIVE")
        self.assertTrue(out["evidence"].get("timeout_neutralised_pass"))

    def test_unauthorized_execution_refused(self):
        eng = re_.RemedyEngine("X", self.budgets, now_fn=self.now,
                               execute=lambda c: {"state": "PASS"}, authorized=False)
        eng.diagnose({"signature": "X"})
        eng.research([cand("A")], {}, [])
        eng.sandbox_and_validate(eng.rank_and_select())
        out = eng.report()
        self.assertEqual(out["stop_condition"], "UNAUTHORIZED_EXECUTION_REQUESTED")
        self.assertEqual(out["execution_state"], "NOT_RUN")

    def test_inconclusive_is_not_refutation(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "kb.jsonl"
            rec = {
                "knowledge_id": "KB-Y", "record_version": 1,
                "created_at": "2026-01-01T00:00:00+00:00",
                "identity": {"investigation_id": "X", "design_id": "d",
                             "design_fingerprint": "f", "source_run": "r"},
                "failure": {"category": "pin_access", "signature": "DRT-0073",
                            "violation_type": "DRT-0073", "tool": "openroad",
                            "technology": "asap7"},
                "root_cause": {"status": "UNKNOWN", "hypothesis": "h"},
                "remedies": [{"remedy_id": "R", "remedy_family": "HYP",
                              "outcome": "INCONCLUSIVE"}],
                "experiment": {"experiment_id": "E", "execution_status": "RUN"},
                "outcome": {"state": "INCONCLUSIVE"},
                "applicability": {"scope": "REUSABLE", "conditions": [], "exclusions": []},
                "evidence": {"observations": [], "inferences": [],
                             "experimentally_supported": [], "validated_knowledge": [],
                             "checksums": {}, "reviewer_findings": []},
                "relationships": {"related_ids": [], "remedy_family": "HYP"},
                "maturity": 0,
                "provenance": {"fde_records": [], "source_hashes": {}},
            }
            p.write_text(json.dumps(rec) + "\n", encoding="utf-8")
            self.assertEqual(re_.kb_refuted_families(p, "DRT-0073"), [])

    def test_no_candidate_above_threshold_is_actionable_gap(self):
        eng = re_.RemedyEngine("X", self.budgets, now_fn=self.now)
        eng.diagnose({"signature": "X"})
        eng.research([cand("A", applicability="PARTIAL", evidence_strength="INFERENCE",
                           effectiveness=0.2)], {}, [])
        self.assertIsNone(eng.rank_and_select())
        out = eng.report()
        self.assertEqual(out["stop_condition"], "CANDIDATES_EXHAUSTED")
        self.assertTrue(out["unresolved_gap"])


if __name__ == "__main__":
    unittest.main()
