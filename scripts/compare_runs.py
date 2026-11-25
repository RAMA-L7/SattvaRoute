#!/usr/bin/env python3
"""Offline attempt comparison from real run evidence (no EDA)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _metrics(run: Path) -> dict[str, Any]:
    reports = run / "work" / "reports"
    out: dict[str, Any] = {}
    cand = list(reports.rglob("6_finish.rpt")) + list(reports.rglob("5_route_drc.rpt"))
    for rpt in cand:
        text = rpt.read_text(encoding="utf-8", errors="replace")
        for key in ("setup violation count", "hold violation count",
                    "max slew violation count", "max fanout violation count",
                    "max cap violation count", "tns max", "wns max",
                    "worst slack max", "period_min"):
            m = re.search(rf"{re.escape(key)}\s+([^\r\n]+)", text, re.I)
            if m:
                out[key] = m.group(1).strip()
        if rpt.name.startswith("5_route_drc"):
            out["drc_report_lines"] = len(text.splitlines())
            out["drc_error_lines"] = sum(
                1 for ln in text.splitlines() if re.search(r"\b(error|violation)\b", ln, re.I))
    results = run / "work" / "results"
    reports = run / "work" / "reports"
    artifacts = ["5_route.odb", "route.guide", "6_final.odb", "6_final.spef",
                 "6_final.def", "6_final.gds"]
    report_files = ["6_finish.rpt", "5_route_drc.rpt"]
    out["artifacts_present"] = {
        **{a: bool(list(results.rglob(a))) for a in artifacts},
        **{r: bool(list(reports.rglob(r))) for r in report_files},
    }
    # An empty DRC report is the expected output for a clean route; confirm
    # via the explicit DRT-0199 count in the stage log.
    route_log = run / "evidence" / "stage_route.log"
    if route_log.is_file():
        text = route_log.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"Number of violations = (\d+)", text)
        out["drt_0199_violation_count"] = int(m.group(1)) if m else None
    return out


def compare(runs: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for label, path in runs.items():
        run = Path(path)
        data = _load(run / "evidence" / "run.json")
        out[label] = {"run_id": data.get("run_id"), "overall_rc": data.get("overall_rc"),
                      "first_failed_stage": data.get("first_failed_stage"),
                      "stages": data.get("stages", []),
                      "engineering_metrics": _metrics(run),
                      "evidence_dir": str(run / "evidence")}
    b = out.get("baseline", {})
    r = out.get("recovery", {})
    if b and r:
        out["comparison"] = {
            "rc_match": b.get("overall_rc") == r.get("overall_rc"),
            "endpoint_artifacts_match": b.get("engineering_metrics", {}).get(
                "artifacts_present") == r.get("engineering_metrics", {}).get(
                "artifacts_present"),
            "drc_report_lines": [b.get("engineering_metrics", {}).get("drc_report_lines"),
                                  r.get("engineering_metrics", {}).get("drc_report_lines")],
        }
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline", required=True)
    p.add_argument("--failure", required=True)
    p.add_argument("--recovery", required=True)
    p.add_argument("--out")
    args = p.parse_args()
    out = compare({"baseline": args.baseline, "failure": args.failure,
                   "recovery": args.recovery})
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                                  encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
