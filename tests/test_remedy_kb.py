#!/usr/bin/env python3
"""Offline tests for the append-only remedy knowledge sidecar. No EDA."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import remedy_kb as rkb  # noqa: E402


def rec(rid, rtype="remedy_candidate", **payload):
    return {"record_id": rid, "type": rtype, "created_at": rkb.utc_now(),
            "payload": payload}


class RemedyKBTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "remedy_ledger.jsonl"
        self.ledger.touch()

    def tearDown(self):
        self.tmp.cleanup()

    def test_chain_verify_and_append_only(self):
        rkb.append_record(self.ledger, rec("R1", family="HAND_CARVE"))
        rkb.append_record(self.ledger, rec("R2", family="GENERATOR"))
        v = rkb.verify(self.ledger)
        self.assertEqual(v["status"], "PASS")
        self.assertEqual(v["records"], 2)
        first = rkb.load_records(self.ledger)[0]
        second = rkb.load_records(self.ledger)[1]
        self.assertEqual(second["prev_hash"], first["record_hash"])

    def test_duplicate_id_rejected(self):
        rkb.append_record(self.ledger, rec("R1"))
        with self.assertRaises(rkb.RemedyKBError):
            rkb.append_record(self.ledger, rec("R1"))
        self.assertEqual(rkb.verify(self.ledger)["records"], 1)

    def test_tamper_detected(self):
        rkb.append_record(self.ledger, rec("R1"))
        path = self.ledger
        lines = path.read_text(encoding="utf-8").splitlines()
        obj = rkb.json.loads(lines[0])
        obj["payload"]["family"] = "TAMPERED"
        path.write_text(rkb.json.dumps(obj, sort_keys=True) + "\n", encoding="utf-8")
        self.assertEqual(rkb.verify(self.ledger)["status"], "FAIL")

    def test_retrieval_traces_record_ids(self):
        rkb.append_record(self.ledger, rec(
            "R1", "research_source", url="https://example.test/pr/1",
            mechanism="DRT-0073 OBS SPACING"))
        rkb.append_record(self.ledger, rec(
            "R2", "research_source", url="https://example.test/pr/2",
            mechanism="unrelated"))
        hits = rkb.retrieve(self.ledger, "DRT-0073 OBS", "research_source")
        self.assertEqual(hits["matches"][0]["record_id"], "R1")
        self.assertTrue(hits["matches"][0]["record_hash"])

    def test_refuted_family_retrieval(self):
        rkb.append_record(self.ledger, rec(
            "F1", "refuted_remedy", family="HAND_CARVE", outcome="REFUTED",
            signature="DRT-0073 pin access"))
        rkb.append_record(self.ledger, rec(
            "F2", "refuted_remedy", family="GENERATOR", outcome="PASS",
            signature="DRT-0073 pin access"))
        fams = rkb.refuted_families(self.ledger, "DRT-0073")
        self.assertEqual(fams, ["HAND_CARVE"])

    def test_inconclusive_not_refuted(self):
        rkb.append_record(self.ledger, rec(
            "F3", "refuted_remedy", family="HYP", outcome="INCONCLUSIVE",
            signature="DRT-0073"))
        self.assertEqual(rkb.refuted_families(self.ledger, "DRT-0073"), [])

    def test_expected_head_check(self):
        rkb.append_record(self.ledger, rec("R1"))
        head = rkb.verify(self.ledger)["head"]
        self.assertEqual(rkb.verify(self.ledger, head)["status"], "PASS")
        self.assertEqual(rkb.verify(self.ledger, "0" * 64)["status"], "FAIL")

    def test_append_refuses_broken_chain(self):
        rkb.append_record(self.ledger, rec("R1"))
        self.ledger.write_text("not json\n", encoding="utf-8")
        with self.assertRaises(rkb.RemedyKBError):
            rkb.append_record(self.ledger, rec("R2"))

    def test_unknown_type_rejected(self):
        with self.assertRaises(rkb.RemedyKBError):
            rkb.append_record(self.ledger, rec("X", "bogus_type"))


if __name__ == "__main__":
    unittest.main()
