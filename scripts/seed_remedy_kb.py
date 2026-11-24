#!/usr/bin/env python3
"""Idempotently seed the remedy-first KB sidecar from knowledge/remedy_seed.jsonl.

Append-only: existing records are never rewritten; only missing record_ids are
added. No EDA, no network, no writes outside the knowledge directory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SEED = ROOT / "knowledge" / "remedy_seed.jsonl"
DEFAULT_LEDGER = ROOT / "knowledge" / "remedy_ledger.jsonl"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", default=str(DEFAULT_SEED))
    p.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    args = p.parse_args()

    ledger = Path(args.ledger)
    if not ledger.exists():
        ledger.touch()
    from remedy_kb import append_record, load_records
    existing = {r.get("record_id") for r in load_records(ledger)}
    added = []
    for line in Path(args.seed).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec["record_id"] in existing:
            continue
        sealed = append_record(ledger, rec)
        added.append(sealed["record_id"])
    print(json.dumps({"status": "PASS", "ledger": str(ledger),
                      "added": added, "total_seed_records": len(added)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
