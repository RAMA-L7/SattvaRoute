#!/usr/bin/env python3
"""SattvaRoute diagnosis evaluation, rubric v3 (successor to frozen v2).

v2 and its recorded results stay unchanged. v3 tightens only correction
identity and scope: exact canonical target, exact replacement value, no corner
tokens anywhere in the change, mandatory variable, and only that variable's
assignment lines in the diff and scratch result. Deterministic, stdlib-only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import evaluate_diagnosis_v2 as v2  # noqa: E402

RUBRIC_VERSION = "t1_rubric/v3"
BASE = v2.RUBRIC_VERSION


def _canonical(path: str, root: str | None) -> str | None:
    p = Path(path)
    if not p.is_absolute():
        p = Path(root or ".") / p
    try:
        return str(p.resolve(strict=False))
    except OSError:
        return None


def strict_validate_correction(output: dict[str, Any], bundle: dict[str, Any],
                               gt: dict[str, Any] | None) -> dict[str, Any]:
    base = v2.validate_correction(output, bundle, gt)
    if base.get("justified_abstention"):
        return base
    gt = gt or {}
    prop = v2._proposal(output)
    problems = list(base.get("problems") or [])
    checks = dict(base.get("checks") or {})

    target = v2._target(prop)
    expected = gt.get("target_file") or gt.get("target") or ""
    roots = gt.get("allowed_roots") or bundle.get("allowed_roots") or []
    if isinstance(roots, str):
        roots = [roots]
    design_root = gt.get("design_root") or bundle.get("design_root")
    if design_root and design_root not in roots:
        roots = list(roots) + [design_root]
    ctarget = _canonical(target, design_root) if target else None
    cexpected = _canonical(expected, design_root) if expected else None
    target_ok = bool(ctarget and cexpected and ctarget == cexpected and
                     (not roots or any(
                         ctarget.startswith(_canonical(r, design_root) or "\0")
                         for r in roots)))
    checks["target"] = target_ok
    if not target_ok:
        problems.append("target is not the exact canonical approved target")

    replacement = v2._replacement(prop)
    expected_value = gt.get("intended_value") or gt.get("replacement_value")
    value_ok = bool(replacement) and expected_value is not None and replacement == expected_value
    checks["replacement_value"] = value_ok
    if expected_value is not None and not value_ok:
        problems.append("replacement value is not an exact match")

    diff = v2._diff(prop)
    corner = v2.CORNER_RE.search("\n".join([replacement, diff, v2._s(prop)]))
    if corner:
        problems.append("corner/operating-point token rejected: " + corner.group(0))

    var = str(prop.get("variable") or prop.get("target_variable") or "")
    if not var:
        problems.append("target variable is mandatory in v3")
    changed = [ln[1:].strip() for ln in diff.splitlines()
               if ln and ln[0] in "+-" and not ln.startswith(("+++", "---"))
               and ln[1:].strip() and not ln[1:].strip().startswith("#")]
    assign = re.compile(r"^(?:export\s+|override\s+)*" + re.escape(var) + r"\s*[+:?]?=")
    if var and changed and not all(assign.match(line) for line in changed):
        problems.append("diff contains a change that is not the target variable assignment")
    if var and changed and expected_value is not None and not any(
            expected_value in line for line in changed):
        problems.append("diff lacks the approved intended value")
    scratch = base.get("scratch_test") or {}
    patched = str(scratch.get("patched_text") or "")
    if expected_value is not None and patched and expected_value not in patched:
        problems.append("scratch-patched result lacks the approved intended value")
    checks["scope"] = not any(p in problems for p in (
        "target variable is mandatory in v3",
        "diff contains a change that is not the target variable assignment",
        "diff lacks the approved intended value",
        "scratch-patched result lacks the approved intended value"))

    return {"status": "correct_repair" if not problems else "incorrect",
            "justified_abstention": False,
            "correct_repair": not problems and not scratch.get("errors"),
            "problems": problems, "checks": checks, "scratch_test": scratch,
            "base_rubric": BASE, "rubric_version": RUBRIC_VERSION}


def grade(output: dict[str, Any], bundle: dict[str, Any],
          gt: dict[str, Any] | None = None) -> dict[str, Any]:
    previous = v2.validate_correction
    v2.validate_correction = strict_validate_correction
    try:
        result = v2.grade(output, bundle, gt)
    finally:
        v2.validate_correction = previous
    result["rubric_version"] = RUBRIC_VERSION
    result["base_rubric"] = BASE
    return result


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
    result = grade(json.loads(Path(args.output).read_text(encoding="utf-8")),
                   json.loads(Path(args.bundle).read_text(encoding="utf-8")),
                   json.loads(Path(args.gt).read_text(encoding="utf-8")) if args.gt else None)
    text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 0 if result.get("diagnosis_accepted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
