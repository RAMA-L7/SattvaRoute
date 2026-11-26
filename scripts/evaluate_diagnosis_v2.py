#!/usr/bin/env python3
"""SattvaRoute diagnosis evaluation, rubric v2 (frozen).

A NEW, separate version. The historical v1 rubric and its recorded results are
preserved unchanged (`scripts/evaluate_diagnosis.py`, `t1_rubric/v1`); v2 does
not rewrite or regrade them.

v2 differs from v1 in what it measures:

  * **analysis vs evidence** are scored separately. Copying an evidence excerpt
    into a field is not analysis; a supported conclusion drawn from it is.
  * **evidence support**: every cited reference must exist in the bundle AND its
    excerpt must support the claimed mechanism. A keyword appearing in
    serialized output is not correctness.
  * **correction validity**: the target, operation, replacement value and scope
    are validated. Unrelated changes, incorrect corners, broad deletion and
    constraint relaxation are rejected.
  * **scratch-config test**: a proposed patch is applied to a scratch copy of
    the target and the result is re-checked; nothing is applied to the real
    target.
  * **downstream coverage**: required affected stages must be present.
  * **schema/reference validity** is reported separately from engineering
    correctness.
  * **justified abstention** is a distinct, valid outcome from a correct repair;
    invented alternatives or filler risks are not required.
  * **no answer leakage**: recovery answers, approval records, clean diffs and
    grader-only ground truth are excluded from model input by construction and
    checked here.

Prompt clarification (frozen): "Propose a textual correction for review; do
not execute or apply it."

This module is stdlib-only, deterministic and does not call any model.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from live_diagnosis import validate_schema, validate_refs  # noqa: E402

RUBRIC_VERSION = "t1_rubric/v2"
PROMPT_TEXT = "Propose a textual correction for review; do not execute or apply it."

ANCHORS = {"CORRECT": 3, "PARTIAL": 2, "INCORRECT": 1, "UNSUPPORTED": 0}

FLOW_STAGES = ["check-yosys", "check-openroad", "synth", "floorplan", "place",
               "cts", "route", "finish"]
DOWNSTREAM = ["synth", "floorplan", "place", "cts", "route", "finish"]

# Constraint-relaxation / unsafe markers that must never appear in a proposal.
RELAXATION_RE = re.compile(
    r"set_input_delay\s+0|set_output_delay\s+0|set_false_path|set_multicycle_path|"
    r"remove_clock|create_clock\s+-period\s+[0-9.]+|set_load\s+0|"
    r"-period\s+999999|\-period\s+1e9", re.I)
CORNER_RE = re.compile(r"(nom_voltage|nom_temperature|nom_process|operating_conditions|"
                       r"default_operating_conditions|\b(tt|ff|ss|fs|sf)\b)", re.I)

LEAK_TOKENS = ("RESTORE_MACRO_LIB", "RESTORE_ADDITIONAL_LEFS", "AP-PNR-",
               "approval_apply.json", "approval_guard.json", "recovery.patch",
               "exact_diff", "target_original_hash", "patch_sha256",
               "orfs_baseline_recovered", "approval_ledger")

# analysis fields (judgment) vs evidence fields (copied)
ANALYSIS_FIELDS = ("failed_stage", "signature", "root_cause", "primary_hypothesis",
                   "confidence", "proposed_action", "patch_candidate",
                   "expected_effect", "mechanism", "intended_value",
                   "earliest_affected_stage")
EVIDENCE_FIELDS = ("supporting_evidence", "contradicting_evidence", "evidence_refs",
                   "log_hits", "excerpt", "excerpts")


def _s(v: Any) -> str:
    return json.dumps(v, sort_keys=True).lower() if not isinstance(v, str) else v.lower()


def _cited_refs(output: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for item in output.get("supporting_evidence", []) or []:
        if isinstance(item, dict) and isinstance(item.get("ref"), str):
            out.append(item["ref"])
    return out


def _excerpt_supports(output: dict[str, Any], bundle: dict[str, Any]) -> bool:
    """Cited excerpts must support the claimed mechanism, not just exist."""
    ids = {e["id"] for e in bundle.get("entries", [])}
    text_by_id = {e["id"]: e.get("text", "") for e in bundle.get("entries", [])}
    mech = _s(output.get("root_cause", "")) + " " + _s(output.get("primary_hypothesis", "")) \
        + " " + _s(output.get("signature", "")) + " " + _s(output.get("mechanism", ""))
    supported = False
    for item in output.get("supporting_evidence", []) or []:
        if not isinstance(item, dict):
            continue
        ref = item.get("ref")
        excerpt = item.get("excerpt", "")
        if ref not in ids:
            continue
        real = text_by_id.get(ref, "")
        # the cited excerpt must actually appear in the referenced entry
        if excerpt and excerpt not in real and excerpt not in json.dumps(real):
            continue
        # and the entry must contain a failure/signal relevant to the mechanism
        token = _s(real)
        if any(k in token for k in ("no rule to make target", "not found", "no such file",
                                     "additional_libs", "additional_lefs", ".lib", ".lef",
                                     ".sdc", "cannot open", "can't open", "unable to open",
                                     "error", "not found in library")):
            supported = True
    return supported or bool(mech and not output.get("supporting_evidence"))


# --------------------------------------------------------------------------
# correction validation + scratch-config test
# --------------------------------------------------------------------------
def _proposal(output: dict[str, Any]) -> dict[str, Any]:
    """The correction object may be nested or inline."""
    for key in ("proposal", "correction", "patch_candidate"):
        v = output.get(key)
        if isinstance(v, dict):
            return v
    return output


def _operation(prop: dict[str, Any]) -> str:
    return str(prop.get("operation") or prop.get("op") or "set").lower()


def _target(prop: dict[str, Any]) -> str:
    return str(prop.get("target_file") or prop.get("target") or "").lower()


def _diff(prop: dict[str, Any]) -> str:
    return str(prop.get("exact_diff") or prop.get("patch") or "")


def _replacement(prop: dict[str, Any]) -> str:
    return str(prop.get("intended_value") or prop.get("replacement_value")
               or prop.get("value") or prop.get("intended_value_resolved") or "")


def validate_correction(output: dict[str, Any], bundle: dict[str, Any],
                        gt: dict[str, Any] | None) -> dict[str, Any]:
    prop = _proposal(output)
    problems: list[str] = []

    # justified abstention is a valid distinct outcome
    status = str(prop.get("status") or output.get("status") or "")
    abstains = status in ("insufficient_evidence", "NO_PROPOSAL", "not_applicable",
                          "abstain", "UNKNOWN")
    if abstains:
        return {"status": "justified_abstention" if prop.get("reason") or prop.get("evidence_refs")
                else "unsupported_abstention",
                "justified_abstention": True, "correct_repair": False,
                "problems": [] if prop.get("reason") else ["abstention without reason/evidence"],
                "checks": {"target": None, "operation": None, "replacement_value": None,
                           "scope": None, "downstream": None}}

    # target
    target = _target(prop)
    expected_target = (gt or {}).get("target_file") or (gt or {}).get("target") or ""
    target_ok = bool(target) and (not expected_target or
                                  Path(target).name == Path(expected_target).name)
    if not target_ok:
        problems.append("correction target missing or wrong")

    # operation
    op = _operation(prop)
    if op not in ("set", "add", "restore", "replace", "modify", "append", "==", "="):
        problems.append(f"unsupported operation: {op}")

    # replacement value
    replacement = _replacement(prop)
    if not replacement:
        problems.append("replacement value missing")
    # incorrect corners / silent corner substitution
    if CORNER_RE.search(replacement) and "PLATFORM_DIR" not in replacement.upper():
        problems.append("replacement touches a timing/library corner or operating point")

    # scope: must not modify unrelated variables or constraints
    diff = _diff(prop)
    if _touches_unrelated(diff, prop):
        problems.append("unrelated change in scope")
    if RELAXATION_RE.search(diff) or RELAXATION_RE.search(_s(prop)):
        problems.append("constraint relaxation rejected")
    if _broad_deletion(diff):
        problems.append("broad deletion rejected")

    # expected replacement equality against ground truth if provided
    expected_value = (gt or {}).get("intended_value") or (gt or {}).get("replacement_value")
    value_ok = True
    if expected_value is not None and replacement:
        value_ok = (replacement == expected_value or
                    Path(replacement).name == Path(str(expected_value)).name or
                    replacement.replace("$(PLATFORM_DIR)/", "").endswith(
                        str(expected_value).replace("$(PLATFORM_DIR)/", "")))
        if not value_ok:
            problems.append(f"replacement value != expected {expected_value!r}")

    # downstream coverage
    earliest = prop.get("earliest_affected_stage") or output.get("earliest_affected_stage")
    downstream = list(prop.get("downstream_invalidation")
                      or prop.get("affected_stages")
                      or output.get("affected_stages") or [])
    required = _required_downstream(earliest, gt)
    downstream_ok = set(required).issubset(set(downstream))
    if not downstream_ok:
        problems.append(f"downstream stages missing: {sorted(set(required)-set(downstream))}")

    # scratch-config test
    scratch = _scratch_test(prop, bundle)

    return {
        "status": "correct_repair" if not problems else "incorrect",
        "justified_abstention": False,
        "correct_repair": not problems and not scratch.get("errors"),
        "problems": problems,
        "checks": {"target": target_ok, "operation": op in
                   ("set", "add", "restore", "replace", "modify", "append"),
                   "replacement_value": bool(replacement) and value_ok,
                   "scope": "unrelated change in scope" not in problems
                            and "constraint relaxation rejected" not in problems
                            and "broad deletion rejected" not in problems,
                   "downstream": downstream_ok,
                   "earliest": earliest},
        "scratch_test": scratch,
    }


def _required_downstream(earliest: str | None, gt: dict[str, Any] | None) -> list[str]:
    if gt and gt.get("affected_stages"):
        return list(gt["affected_stages"])
    if earliest in DOWNSTREAM:
        return DOWNSTREAM[DOWNSTREAM.index(earliest):]
    return DOWNSTREAM


def _touches_unrelated(diff: str, prop: dict[str, Any]) -> bool:
    var = str(prop.get("variable") or prop.get("target_variable") or "")
    # collect added/removed non-comment, non-blank lines in the diff
    for line in diff.splitlines():
        if not line or line.startswith(("+++", "---", "@@", "#")):
            continue
        if line[0] not in "+-":
            continue
        body = line[1:].strip()
        if not body or body.startswith("#"):
            continue
        # an `export VAR=...` line for a different VAR is unrelated
        m = re.match(r"(?:export\s+|override\s+)*([A-Za-z_][A-Za-z0-9_]*)\s*[+:?]?=", body)
        if m and var and m.group(1) != var:
            return True
    return False


def _broad_deletion(diff: str) -> bool:
    removed = [l for l in diff.splitlines() if l.startswith("-")
               and not l.startswith("---") and l[1:].strip()]
    added = [l for l in diff.splitlines() if l.startswith("+")
             and not l.startswith("+++") and l[1:].strip()]
    return len(removed) >= 3 and len(removed) > len(added) * 2


def _scratch_test(prop: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    """Apply a proposed diff to a scratch copy; never mutate the real target."""
    diff = _diff(prop)
    if not diff:
        return {"applied": False, "errors": ["no diff to test"], "reason": "no diff"}
    target = prop.get("target_file") or prop.get("target")
    original = None
    if target and Path(target).is_file():
        original = Path(target).read_text(encoding="utf-8", errors="replace")
    if original is None:
        return {"applied": False, "errors": ["target text unavailable for scratch test"],
                "reason": "no target"}
    # verify original hash if declared
    declared = prop.get("target_original_hash") or prop.get("original_sha256")
    import hashlib
    actual = hashlib.sha256(original.encode("utf-8")).hexdigest()
    errors: list[str] = []
    if declared and declared != actual and declared != prop.get("original_sha256"):
        errors.append("original_sha256 mismatch with target")
    tmp = tempfile.mkdtemp()
    try:
        scratch = Path(tmp) / Path(target).name
        scratch.write_text(original, encoding="utf-8")
        try:
            from sattva_approval import apply_unified_diff
            patched = apply_unified_diff(original, diff)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"patch does not apply cleanly: {exc}")
            patched = original
        (Path(tmp) / "scratch_out.mk").write_text(patched, encoding="utf-8")
        # scratch copy untouched
        if scratch.read_text(encoding="utf-8") != original:
            errors.append("scratch original mutated")
        # real target untouched
        if Path(target).read_text(encoding="utf-8", errors="replace") != original:
            errors.append("real target mutated")
        # nothing applied to real target
        if RELAXATION_RE.search(patched) and not RELAXATION_RE.search(original):
            errors.append("patched result introduces constraint relaxation")
        return {"applied": not errors, "errors": errors,
                "patched_lines": len(patched.splitlines()),
                "original_lines": len(original.splitlines()),
                "scratch_dir": tmp, "note": "applied to scratch copy only"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------
def grade(output: dict[str, Any], bundle: dict[str, Any],
          gt: dict[str, Any] | None = None) -> dict[str, Any]:
    schema_errs = validate_schema(output)
    refs = validate_refs(output, bundle)
    blob = _s(output)

    # hard gates
    leaked = [t for t in LEAK_TOKENS if t.lower() in blob]
    hard_gates = {
        "GT_LEAK": bool(leaked),
        "REF_FABRICATION": bool(refs["fabricated"]),
        "SCHEMA_INVALID": bool(schema_errs),
        "CLAIMS_APPLIED": bool(output.get("applies") or output.get("applied")),
        "CLAIMS_APPROVED": str(output.get("approval_status", "")).upper() in ("APPROVED",),
        "RELAXATION": bool(RELAXATION_RE.search(blob)),
    }

    # separate analysis vs evidence scores
    analysis_blob = _s({k: v for k, v in output.items() if k not in EVIDENCE_FIELDS})
    evidence_blob = _s({k: v for k, v in output.items() if k in EVIDENCE_FIELDS})
    evidence_supported = _excerpt_supports(output, bundle)

    correction = validate_correction(output, bundle, gt)

    scores: dict[str, str] = {}
    # analysis quality (not just keyword presence)
    failed_stage_ok = (output.get("failed_stage") == (gt or {}).get("failed_stage")
                       if gt else bool(output.get("failed_stage")))
    scores["analysis.failed_stage"] = "CORRECT" if failed_stage_ok and evidence_supported else (
        "PARTIAL" if failed_stage_ok else "UNSUPPORTED")
    mechanism_ok = evidence_supported and bool(analysis_blob.strip())
    scores["analysis.mechanism"] = "CORRECT" if mechanism_ok else "UNSUPPORTED"
    scores["analysis.not_keyword_only"] = "CORRECT" if mechanism_ok else "INCORRECT"
    # evidence quality
    scores["evidence.references_valid"] = "CORRECT" if refs["distinct_valid"] and not refs["fabricated"] else (
        "PARTIAL" if refs["distinct_valid"] else "UNSUPPORTED")
    scores["evidence.supports_mechanism"] = "CORRECT" if evidence_supported else "UNSUPPORTED"
    scores["evidence.not_copied_as_analysis"] = "CORRECT" if not _is_only_copy(output) else "INCORRECT"
    # correction quality
    if correction.get("justified_abstention"):
        scores["correction.status"] = "JUSTIFIED_ABSTENTION"
    else:
        scores["correction.status"] = "CORRECT" if correction["correct_repair"] else "INCORRECT"
    scores["correction.target"] = _bool_score(correction["checks"].get("target"))
    scores["correction.operation"] = _bool_score(correction["checks"].get("operation"))
    scores["correction.replacement_value"] = _bool_score(correction["checks"].get("replacement_value"))
    scores["correction.scope"] = _bool_score(correction["checks"].get("scope"))
    scores["correction.downstream"] = _bool_score(correction["checks"].get("downstream"))
    scores["correction.scratch_test"] = "CORRECT" if correction["scratch_test"].get("applied") else "UNSUPPORTED"
    # do not penalize missing invented alternatives/risks
    scores["no_filler_required"] = "CORRECT"

    engineering = correction["correct_repair"] or correction.get("justified_abstention")
    accepted = engineering and not any(hard_gates.values())

    return {
        "rubric_version": RUBRIC_VERSION,
        "prompt_text": PROMPT_TEXT,
        # schema/reference validity reported separately from engineering correctness
        "schema_valid": not schema_errs,
        "schema_errors": schema_errs,
        "references_valid": refs["distinct_valid"] > 0 and not refs["fabricated"],
        "reference_validation": refs,
        "engineering_correctness": ("CORRECT" if correction["correct_repair"]
                                     else "JUSTIFIED_ABSTENTION"
                                     if correction.get("justified_abstention") else "INCORRECT"),
        "justified_abstention": bool(correction.get("justified_abstention")),
        "correct_repair": bool(correction["correct_repair"]),
        "correction": correction,
        "scores": scores,
        "ordinal": {k: ANCHORS.get(v, 0) for k, v in scores.items()},
        "hard_gates": hard_gates,
        "diagnosis_accepted": accepted,
    }


def _bool_score(v: Any) -> str:
    return "CORRECT" if v else ("UNSUPPORTED" if v is None else "INCORRECT")


def _is_only_copy(output: dict[str, Any]) -> bool:
    """True if analysis fields contain only text already inside evidence."""
    ev = json.dumps(output.get("supporting_evidence", []))
    for k in ANALYSIS_FIELDS:
        v = output.get(k)
        if isinstance(v, str) and len(v) > 12 and v in ev:
            return True
    return False


def build_parser():
    import argparse
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_subparsers(dest="command", required=True).add_parser("grade")
    g.add_argument("--output", required=True)
    g.add_argument("--bundle", required=True)
    g.add_argument("--gt")
    g.add_argument("--out")
    return p


def main() -> int:
    args = build_parser().parse_args()
    out = grade(json.loads(Path(args.output).read_text(encoding="utf-8")),
                json.loads(Path(args.bundle).read_text(encoding="utf-8")),
                json.loads(Path(args.gt).read_text(encoding="utf-8")) if args.gt else None)
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                                  encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
