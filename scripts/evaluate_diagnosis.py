#!/usr/bin/env python3
"""Deterministic baseline diagnosis and transparent ordinal evaluation.

Both modes are graded by the same code against a grader-only ground-truth
record. The prompt/bundle path never reads ground truth.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from live_diagnosis import validate_schema, validate_refs

ANCHORS = {"CORRECT": 3, "PARTIAL": 2, "INCORRECT": 1, "UNSUPPORTED": 0}
METRICS = ("failure_stage", "signature", "root_cause", "evidence_precision",
           "evidence_completeness", "contradiction_handling", "alternative_quality",
           "patch_correctness", "patch_scope", "stage_selection",
           "risk_identification", "unsupported_claims")
FLOW_STAGES = ["check-yosys", "check-openroad", "synth", "floorplan", "place",
               "cts", "route", "finish"]


def _text(bundle: dict[str, Any], eid: str) -> str:
    return next(e["text"] for e in bundle["entries"] if e["id"] == eid)


def deterministic_output(bundle: dict[str, Any]) -> dict[str, Any]:
    """Rule-based diagnosis from evidence bundle only; no ground-truth reads."""
    e01, e02, e03, e04, e05, e06 = (_text(bundle, f"E{i:02d}") for i in range(1, 7))
    stage = "synth" if re.search(r'"first_failed_stage"\s*:\s*"synth"', e01) else "UNKNOWN"
    missing = re.search(r"([^\s'\"]*missing_[A-Za-z0-9_]+\.lib)", e03)
    correct = re.search(r"export ADDITIONAL_LIBS\s*=\s*(\$\(PLATFORM_DIR\)/\S+\.lib)", e05)
    ref = lambda eid, text: {"ref": eid, "excerpt": _text(bundle, eid)}
    return {
        "item_id": bundle["bundle_id"], "mode": "deterministic",
        "execution_kind": "rule_based",
        "failure_class": "missing macro Liberty reference",
        "failed_stage": stage,
        "primary_hypothesis": (
            f"attempt-local config resolves {missing.group(1) if missing else 'a macro Liberty file'} "
            "to a nonexistent path; synth make fails"),
        "supporting_evidence": [ref("E01", e01), ref("E02", e02),
                                ref("E03", e03), ref("E04", e04), ref("E05", e05)],
        "contradicting_evidence": [
            {"claim": "prechecks passed, so inputs are valid",
             "why_not_decisive": "precheck success is not stage success",
             "ref": "E02", "excerpt": e02}],
        "alternative_hypotheses": [
            {"cause": "missing standard-cell Liberty", "why_rejected": "E03 names the macro lib path"},
            {"cause": "SDC timing error", "why_rejected": "failure occurs at make input resolution"}],
        "confidence": "high",
        "proposed_action": "restore the pinned platform macro Liberty declaration in the attempt-local config",
        "patch_candidate": (f"in attempt-local design/config.mk, replace the invalid "
                            f"ADDITIONAL_LIBS line with export ADDITIONAL_LIBS = "
                            f"{correct.group(1) if correct else 'UNKNOWN'}"),
        "expected_effect": "synth resolves the macro Liberty and downstream stages can run",
        "affected_stages": [s for s in FLOW_STAGES if s not in ("check-yosys", "check-openroad")],
        "risk_assessment": [
            "other macro views may also diverge from the benchmark",
            "timing/congestion may change after restoring the macro model"],
        "verification_plan": ["isolated rerun", "compare DRC/timing with baseline"],
        "missing_information": ["no recovery evidence is available in the model input"],
    }


def _cited_refs(output: dict[str, Any]) -> list[str]:
    out = []
    for item in output.get("supporting_evidence", []):
        if isinstance(item, dict) and isinstance(item.get("ref"), str):
            out.append(item["ref"])
    return out


def grade(output: dict[str, Any], bundle: dict[str, Any],
          gt: dict[str, Any]) -> dict[str, Any]:
    scores: dict[str, str] = {}
    reasons: dict[str, str] = {}
    refs = validate_refs(output, bundle)
    cited = _cited_refs(output)
    distinct = set(cited)
    blob = json.dumps(output, sort_keys=True).lower()

    def set_score(name: str, value: str, reason: str) -> None:
        scores[name] = value
        reasons[name] = reason

    set_score("failure_stage",
              "CORRECT" if output.get("failed_stage") == gt["failed_stage"] and refs["distinct_valid"]
              else "PARTIAL" if output.get("failed_stage") == gt["failed_stage"]
              else "INCORRECT" if output.get("failed_stage") else "UNSUPPORTED",
              "E01/E02 stage resolution")

    sig_ok = "missing_fakeram45_64x32.lib" in blob or "macro liberty" in blob
    sig_config = "additional_libs" in blob or "config.mk" in blob
    sig_make = "no rule to make target" in blob or "synth" in blob
    sig_hits = sum((sig_ok, sig_config, sig_make))
    set_score("signature", ("CORRECT" if sig_hits == 3 else "PARTIAL" if sig_hits == 2
                            else "INCORRECT" if sig_hits == 1 else "UNSUPPORTED"),
              f"signature elements {sig_hits}/3")

    rc_a = "additional_libs" in blob and "attempt-local" in blob
    rc_b = make_ok = "no rule to make target" in blob or "nonexistent" in blob
    rc_c = "benchmark" in blob or "platform_dir" in blob
    rc_hits = sum((rc_a, rc_b, rc_c))
    set_score("root_cause", ("CORRECT" if rc_hits == 3 and refs["distinct_valid"]
                             else "PARTIAL" if rc_hits >= 2 else "INCORRECT" if rc_hits == 1
                             else "UNSUPPORTED"), f"root-cause elements {rc_hits}/3")

    precision = (refs["distinct_valid"] / len(cited)) if cited else 0.0
    set_score("evidence_precision",
              "UNSUPPORTED" if refs["fabricated"] else
              "CORRECT" if precision == 1.0 and refs["distinct_valid"] >= 3 else
              "PARTIAL" if precision >= 0.8 or refs["distinct_valid"] >= 3 else
              "INCORRECT" if precision >= 0.5 else "UNSUPPORTED",
              f"valid/distinct={refs['distinct_valid']}/{len(cited)}")

    required = {"E01", "E02", "E03", "E04", "E05"}
    covered = required & distinct
    set_score("evidence_completeness",
              "UNSUPPORTED" if refs["fabricated"] else
              "CORRECT" if len(covered) == len(required) else
              "PARTIAL" if len(covered) >= 4 else
              "INCORRECT" if len(covered) >= 2 else "UNSUPPORTED",
              f"required covered {len(covered)}/{len(required)}")

    contradictions = output.get("contradicting_evidence", [])
    set_score("contradiction_handling",
              "CORRECT" if len(contradictions) >= 1 and "precheck" in blob else
              "PARTIAL" if contradictions else "UNSUPPORTED",
              "contradiction records and precheck caveat")

    alts = output.get("alternative_hypotheses", [])
    evidenced = sum(1 for a in alts if isinstance(a, dict) and a.get("why_rejected"))
    set_score("alternative_quality",
              "CORRECT" if evidenced >= 2 else "PARTIAL" if evidenced >= 1 else "UNSUPPORTED",
              f"{evidenced} evidenced alternatives")

    patch = str(output.get("patch_candidate", ""))
    set_score("patch_correctness",
              "CORRECT" if "additional_libs" in patch.lower() and "platform_dir" in patch.lower()
              else "INCORRECT" if patch else "UNSUPPORTED",
              "patch line checks")

    set_score("patch_scope",
              "CORRECT" if "config.mk" in patch.lower() and "additional_libs" in patch.lower()
              else "INCORRECT" if patch else "UNSUPPORTED",
              "attempt-local config only")

    stages = output.get("affected_stages", [])
    expected = gt["affected_stages"]
    set_score("stage_selection",
              "CORRECT" if stages == expected else
              "PARTIAL" if stages and stages[0] == expected[0] else
              "INCORRECT" if stages else "UNSUPPORTED",
              "stage set/order equality")

    risks = output.get("risk_assessment", [])
    set_score("risk_identification",
              "CORRECT" if len(risks) >= 2 else "PARTIAL" if risks else "UNSUPPORTED",
              f"{len(risks)} risks")

    set_score("unsupported_claims",
              "CORRECT" if not refs["fabricated"] else "UNSUPPORTED",
              "fabricated references; explicit missing_information is expected, not penalized")

    leak_tokens = ("RESTORE_MACRO_LIB", "AP-PNR-", "proposal.json", "recovery.patch",
                   "comparison.json", "orfs_baseline_recovered", "3205f326", "8a7178f6")
    hard_gates = {"GT_LEAK": any(t.lower() in blob for t in leak_tokens),
                  "REF_FABRICATION": bool(refs["fabricated"]),
                  "SCHEMA_INVALID": bool(validate_schema(output))}
    accepted = (all(scores[m] in ("CORRECT", "PARTIAL")
                    for m in ("failure_stage", "root_cause", "patch_correctness",
                              "stage_selection"))
                and scores["unsupported_claims"] != "UNSUPPORTED"
                and not any(hard_gates.values()))
    return {"scores": scores, "ordinal": {k: ANCHORS[v] for k, v in scores.items()},
            "reasons": reasons, "hard_gates": hard_gates,
            "reference_validation": refs, "diagnosis_accepted": accepted,
            "rubric_version": "t1_rubric/v1"}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("deterministic")
    d.add_argument("--bundle", required=True)
    d.add_argument("--out")
    d.set_defaults(func=lambda a: deterministic_output(
        json.loads(Path(a.bundle).read_text(encoding="utf-8"))))
    g = sub.add_parser("grade")
    g.add_argument("--output", required=True)
    g.add_argument("--bundle", required=True)
    g.add_argument("--gt", required=True)
    g.add_argument("--out")
    g.set_defaults(func=lambda a: grade(
        json.loads(Path(a.output).read_text(encoding="utf-8")),
        json.loads(Path(a.bundle).read_text(encoding="utf-8")),
        json.loads(Path(a.gt).read_text(encoding="utf-8"))))
    return p


def main() -> int:
    args = build_parser().parse_args()
    out = args.func(args)
    if getattr(args, "out", None):
        Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                                  encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
