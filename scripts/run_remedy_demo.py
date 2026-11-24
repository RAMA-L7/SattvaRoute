#!/usr/bin/env python3
"""DRT-0073 demonstration of the remedy-first workflow. NO EDA.

The demonstration reuses ENG009-ENG015 evidence through the remedy KB sidecar,
ranks the known candidate families, and shows the engine stopping at the
physical-legality / evidence gate instead of executing an unverified remedy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = ROOT / "knowledge" / "remedy_ledger.jsonl"
DEFAULT_OUT = ROOT / "experiments" / "WF-DEMO" / "T-WORKFLOW-001" / "remedy_demo.json"

# Candidate descriptions are taken verbatim from ENG015 research; no new
# remedy is proposed and no geometry is designed here.
CANDIDATES = [
    {"candidate_id": "C-BROAD", "family": "BROAD_OBS_CARVE",
     "mechanism": "remove full M4 OBS interior to clear probe neighbourhood",
     "evidence_strength": "DOCUMENTED_FIX", "applicability": "EXACT",
     "effectiveness": 0.95, "risk": 1.0, "cost_minutes": 30,
     "reversibility": "NONE", "legality": "FAIL",
     "predicted_outcome": "W clean 3/3, 3 APs (observed) but physically illegal",
     "sources": ["docs/ENG012_BROAD_CARVE_PROVENANCE.md"]},
    {"candidate_id": "C-HAND", "family": "HAND_OBS_CARVE",
     "mechanism": "narrow per-pin M4 OBS corridor / exact west strip",
     "evidence_strength": "DIRECT_EXPERIENCE", "applicability": "EXACT",
     "effectiveness": 0.2, "risk": 0.9, "cost_minutes": 45,
     "reversibility": "FULL", "legality": "FAIL",
     "predicted_outcome": "0 APs (observed in R1-N/R1-N-W/C1/C2)",
     "sources": ["docs/ENG011_DIAGNOSTIC_RESULTS.md"]},
    {"candidate_id": "C-Y", "family": "Y_ENVELOPE",
     "mechanism": "widen OBS corridor in y to satisfy EOL envelope",
     "evidence_strength": "DIRECT_EXPERIENCE", "applicability": "EXACT",
     "effectiveness": 0.1, "risk": 0.8, "cost_minutes": 45,
     "reversibility": "FULL", "legality": "FAIL",
     "predicted_outcome": "0 APs (observed)",
     "sources": ["docs/ENG011_DIAGNOSTIC_RESULTS.md"]},
    {"candidate_id": "C-PIN", "family": "PIN_GEOMETRY",
     "mechanism": "widen or translate LEF pin rectangle",
     "evidence_strength": "INFERENCE", "applicability": "PARTIAL",
     "effectiveness": 0.2, "risk": 0.9, "cost_minutes": 120,
     "reversibility": "NONE", "legality": "FAIL",
     "predicted_outcome": "no demonstrated W access",
     "sources": ["docs/ENG014_REMEDY_CLASS_MATRIX.md"]},
    {"candidate_id": "C-PLACE", "family": "PLACEMENT",
     "mechanism": "macro translation / grid alignment",
     "evidence_strength": "DIRECT_EXPERIENCE", "applicability": "INCOMPATIBLE",
     "effectiveness": 0.0, "risk": 0.7, "cost_minutes": 60,
     "reversibility": "FULL", "legality": "PASS",
     "predicted_outcome": "no change: relative pin-to-OBS geometry invariant",
     "sources": ["docs/ENG014_REMEDY_CLASS_MATRIX.md"]},
    {"candidate_id": "C-CONFIG", "family": "CONFIG_FLAG",
     "mechanism": "via-in-pin / threshold / other pin_access flags",
     "evidence_strength": "DIRECT_EXPERIENCE", "applicability": "INCOMPATIBLE",
     "effectiveness": 0.0, "risk": 0.4, "cost_minutes": 15,
     "reversibility": "FULL", "legality": "PASS",
     "predicted_outcome": "no effect (observed)",
     "sources": ["docs/ENG014_REMEDY_CLASS_MATRIX.md"]},
    {"candidate_id": "C-OBSSEM", "family": "OBS_SPACING_SEMANTICS",
     "mechanism": "OBS SPACING 0 / USEMINSPACING OBS ON",
     "evidence_strength": "DOCUMENTED_FIX", "applicability": "INCOMPATIBLE",
     "effectiveness": 0.05, "risk": 0.4, "cost_minutes": 20,
     "reversibility": "FULL", "legality": "UNKNOWN",
     "predicted_outcome": "no effect on true overlap Short (source-proven)",
     "sources": ["https://github.com/The-OpenROAD-Project/OpenROAD/pull/10856"]},
    {"candidate_id": "C-FILTER", "family": "ILLEGAL_MARKER_FILTERING",
     "mechanism": "filter OBS-only PA markers / re-own OBS to pin net",
     "evidence_strength": "INFERENCE", "applicability": "PARTIAL",
     "effectiveness": 0.5, "risk": 1.0, "cost_minutes": 60,
     "reversibility": "PARTIAL", "legality": "FAIL",
     "predicted_outcome": "could mask real shorts; fails legality gate",
     "sources": ["docs/ENG015_RESEARCH_GATE.md"]},
    {"candidate_id": "C-EXT", "family": "EXTENDED_WEST_CARVE",
     "mechanism": "west OBS edge moved to x<=3461 with 72 nm y window",
     "evidence_strength": "INFERENCE", "applicability": "PARTIAL",
     "effectiveness": 0.55, "risk": 0.85, "cost_minutes": 60,
     "reversibility": "FULL", "legality": "UNKNOWN",
     "predicted_outcome": "W clean plausible, all-pin success unknown",
     "sources": ["docs/ENG015_CANDIDATE_COMPARISON.md"],
     "prerequisites": ["GDS foreign-net census x3445-3474", "rule-envelope proof",
                       "all-pin AP survey", "fresh approval"]},
    {"candidate_id": "C-GEN", "family": "GENERATOR_OBS_REGEN",
     "mechanism": "generator-level pin-aware OBS regeneration for all pins",
     "evidence_strength": "DOCUMENTED_FIX", "applicability": "HIGH",
     "effectiveness": 0.7, "risk": 0.8, "cost_minutes": 240,
     "reversibility": "PARTIAL", "legality": "UNKNOWN",
     "predicted_outcome": "principled all-pin fix, unevidenced",
     "sources": ["https://github.com/The-OpenROAD-Project/OpenROAD/pull/9935"],
     "prerequisites": ["generator configurability proof", "GDS vacancy per pin",
                       "all-pin AP", "full-flow signoff", "fresh approval"]},
]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()

    from remedy_engine import (RemedyEngine, Candidate, load_budgets,
                               kb_refuted_families)
    from remedy_kb import refuted_families

    budgets = load_budgets()
    ledger_refuted = refuted_families(args.ledger, "DRT-0073")
    kb_refuted = kb_refuted_families(ROOT / "knowledge" / "kb_records.jsonl",
                                     "DRT-0073")
    refuted = sorted(set(ledger_refuted) | set(kb_refuted))

    candidates = [Candidate(**c) for c in CANDIDATES]
    sources = {c["candidate_id"]: c["sources"] for c in CANDIDATES}

    eng = RemedyEngine("DRT-0073", budgets)
    eng.diagnose({"signature": "DRT-0073 u_sram/clk",
                  "source": "docs/ENG013_BLOCKER_ATTRIBUTION.md",
                  "reused": True})
    eng.research(candidates, sources, refuted)
    selected = eng.rank_and_select()
    if selected is not None:
        eng.sandbox_and_validate(selected)  # no execute callback -> NOT_RUN
    else:
        eng.skip_execution("no candidate passed the evidence/legality gate")
    report = eng.report()
    from remedy_kb import verify
    kb_write = eng.report_kb(args.ledger, "WF-RUN-DRT0073-001")
    report["kb_write"] = kb_write
    report["ledger_head"] = verify(args.ledger)["head"]
    report["workflow"] = "FAILURE->DIAGNOSIS->KB+WEB->RANK->SELECT->SANDBOX->VALIDATE->REPORT+KB"
    report["eda_executed"] = False

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": "PASS", "out": str(out),
                      "stop_condition": report["stop_condition"],
                      "selection": report["selection"],
                      "execution_state": report["execution_state"],
                      "ranked_count": len(report["ranked"]),
                      "eda_executed": False}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
