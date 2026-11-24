#!/usr/bin/env python3
"""Append-only remedy-first knowledge sidecar for SattvaRoute.

This EXTENDS the existing KB (scripts/sattva_kb.py) without replacing or
rewriting it. The existing ledger remains authoritative for investigation
records; this sidecar adds the structured remedy-first record types that the
current schema cannot express:

  failure_signature, root_cause, tool_context, research_source,
  remedy_candidate, successful_fix, refuted_remedy, experiment_config,
  baseline_treatment_metrics, regression_result, resolution_time,
  engineering_conclusion

Properties:
  * append-only with SHA-256 hash chaining (same pattern as sattva_kb.py);
  * no EDA, no network, no writes outside the knowledge directory;
  * retrieval tokenises payload text and returns record IDs + hashes so every
    recommendation traces to a stored record;
  * refuted-remedy retrieval is first-class so the engine can eliminate
    previously failed approaches automatically.

Usage:
  python3 scripts/remedy_kb.py init --ledger knowledge/remedy_ledger.jsonl
  python3 scripts/remedy_kb.py append --ledger ... --record file.json
  python3 scripts/remedy_kb.py verify --ledger ...
  python3 scripts/remedy_kb.py retrieve --ledger ... --query 'DRT-0073 OBS' [--type refuted_remedy]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = ROOT / "knowledge" / "remedy_ledger.jsonl"

RECORD_TYPES = (
    "failure_signature", "root_cause", "tool_context", "research_source",
    "remedy_candidate", "successful_fix", "refuted_remedy", "experiment_config",
    "baseline_treatment_metrics", "regression_result", "resolution_time",
    "engineering_conclusion",
)
REFUTED_TYPES = {"refuted_remedy", "successful_fix"}
STOPWORDS = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "or",
             "with", "from", "that", "this", "was", "were", "are", "is"}


class RemedyKBError(Exception):
    pass


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_records(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    out = []
    for lineno, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise RemedyKBError(f"invalid JSON at line {lineno}: {exc}") from exc
    return out


def seal(record: dict[str, Any], prev_hash: str) -> dict[str, Any]:
    sealed = dict(record)
    sealed["prev_hash"] = prev_hash
    body = json.dumps({k: v for k, v in sealed.items() if k != "record_hash"},
                      sort_keys=True, separators=(",", ":"))
    sealed["record_hash"] = sha256_text(body)
    return sealed


def last_hash(records: list[dict[str, Any]]) -> str:
    return records[-1].get("record_hash", "0" * 64) if records else "0" * 64


def validate_record(rec: dict[str, Any]) -> None:
    required = ("record_id", "type", "created_at", "payload")
    missing = [k for k in required if k not in rec]
    if missing:
        raise RemedyKBError(f"record missing keys: {missing}")
    if rec["type"] not in RECORD_TYPES:
        raise RemedyKBError(f"unknown record type: {rec['type']}")
    if not isinstance(rec["payload"], dict):
        raise RemedyKBError("payload must be a JSON object")


def append_record(ledger: str | Path, record: dict[str, Any]) -> dict[str, Any]:
    validate_record(record)
    # Never chain onto a corrupted ledger.
    if Path(ledger).exists() and verify(ledger)["status"] != "PASS":
        raise RemedyKBError("ledger chain invalid; refusing append")
    records = load_records(ledger)
    ids = {r.get("record_id") for r in records}
    if record["record_id"] in ids:
        raise RemedyKBError(f"duplicate record_id: {record['record_id']}")
    sealed = seal(record, last_hash(records))
    path = Path(ledger)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(sealed, sort_keys=True, separators=(",", ":")) + "\n")
    return sealed


def verify(ledger: str | Path, expected_head: str | None = None) -> dict[str, Any]:
    records = load_records(ledger)
    problems: list[str] = []
    prev = "0" * 64
    ids: set[str] = set()
    for idx, rec in enumerate(records, 1):
        try:
            validate_record(rec)
        except RemedyKBError as exc:
            problems.append(f"line {idx}: {exc}")
            continue
        rid = rec["record_id"]
        if rid in ids:
            problems.append(f"line {idx}: duplicate record_id {rid}")
        ids.add(rid)
        if rec.get("prev_hash") != prev:
            problems.append(f"line {idx}: prev_hash mismatch")
        body = json.dumps({k: v for k, v in rec.items() if k != "record_hash"},
                          sort_keys=True, separators=(",", ":"))
        if sha256_text(body) != rec.get("record_hash"):
            problems.append(f"line {idx}: record_hash mismatch")
        prev = rec.get("record_hash", prev)
    if expected_head is not None and prev != expected_head:
        problems.append(f"head mismatch: expected {expected_head}, got {prev}")
    return {"status": "PASS" if not problems else "FAIL",
            "records": len(records), "problems": problems,
            "head": prev}


def _tokens(text: str) -> set[str]:
    # Strip JSON punctuation so payload keys/values tokenise consistently.
    return {t for t in re.findall(r"[a-z0-9][a-z0-9\-]*",
                                  text.lower().replace("_", " "))
            if len(t) > 2 and t not in STOPWORDS}


def retrieve(ledger: str | Path, query: str,
             record_type: str | None = None, limit: int = 20) -> dict[str, Any]:
    q = _tokens(query)
    hits = []
    for rec in load_records(ledger):
        if record_type and rec.get("type") != record_type:
            continue
        hay = _tokens(json.dumps(rec.get("payload", {}), sort_keys=True)
                      + " " + str(rec.get("type", "")))
        score = len(q & hay)
        if score:
            hits.append({"record_id": rec["record_id"], "type": rec["type"],
                         "score": score, "record_hash": rec["record_hash"],
                         "payload": rec["payload"]})
    hits.sort(key=lambda h: (-h["score"], h["record_id"]))
    return {"status": "PASS", "query": query, "type": record_type,
            "matches": hits[:limit], "total": len(hits)}


def refuted_families(ledger: str | Path, signature: str = "") -> list[str]:
    """Return families marked refuted/failed, optionally signature-scoped."""
    out: set[str] = set()
    q = _tokens(signature)
    for rec in load_records(ledger):
        if rec.get("type") not in REFUTED_TYPES:
            continue
        payload = rec.get("payload", {})
        if payload.get("outcome") not in {"FAIL", "REFUTED", "REJECTED"}:
            continue
        hay = _tokens(json.dumps(payload, sort_keys=True))
        if q and not (q & hay):
            continue
        fam = payload.get("remedy_family") or payload.get("family")
        if fam:
            out.add(str(fam))
    return sorted(out)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    i = sub.add_parser("init")
    i.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    i.set_defaults(func=lambda a: {"status": "PASS" if Path(a.ledger).exists()
                                   else "FAIL"})
    a = sub.add_parser("append")
    a.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    a.add_argument("--record", required=True)
    a.set_defaults(func=lambda a: append_record(
        a.ledger, json.loads(Path(a.record).read_text(encoding="utf-8"))))
    v = sub.add_parser("verify")
    v.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    v.add_argument("--expected-head", default=None)
    v.set_defaults(func=lambda a: verify(a.ledger, a.expected_head))
    r = sub.add_parser("retrieve")
    r.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    r.add_argument("--query", required=True)
    r.add_argument("--type", dest="record_type", choices=RECORD_TYPES)
    r.add_argument("--limit", type=int, default=20)
    r.set_defaults(func=lambda a: retrieve(a.ledger, a.query, a.record_type, a.limit))
    f = sub.add_parser("refuted")
    f.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    f.add_argument("--signature", default="")
    f.set_defaults(func=lambda a: {"status": "PASS",
                                   "families": refuted_families(a.ledger, a.signature)})
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "init":
        Path(args.ledger).touch()
        print(json.dumps({"status": "PASS", "ledger": args.ledger}))
        return 0
    out = args.func(args)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out.get("status", "PASS") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
