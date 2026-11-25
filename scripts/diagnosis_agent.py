#!/usr/bin/env python3
"""Failure classification and reviewable patch proposal.

Deterministic parsing/classification is deliberately separate from any
model-generated narrative. If SATTVA_MODEL_URL is configured, an optional
OpenAI-compatible chat-completions request adds a `model_note`; otherwise the
proposal is explicitly labelled deterministic. No hard-coded fixture response
is presented as live model reasoning.
"""
from __future__ import annotations

import dataclasses
import difflib
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def classify_failure(run_dir: str | Path) -> dict[str, Any]:
    """Read real run evidence; never infer success from rc alone."""
    run = Path(run_dir)
    ev = run / "evidence"
    stages: list[dict[str, Any]] = []
    tsv = ev / "stages.tsv"
    if tsv.is_file():
        for line in tsv.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                stages.append({"stage": parts[0], "rc": parts[1]})
    failed = next((s for s in stages if s["rc"] not in ("0", "RESUMED")), None)
    log_hits: list[dict[str, Any]] = []
    for log in sorted(ev.glob("stage_*.log")):
        text = log.read_text(encoding="utf-8", errors="replace")
        for pat in (r"DRT-\d+[^\n]*", r"[^\n]*not found in library[^\n]*",
                    r"[^\n]*No access point[^\n]*",
                    r"[^\n]*missing_fakeram[^\n]*",
                    r"[^\n]*No such file or directory[^\n]*",
                    r"[^\n]*ERROR[^\n]*"):
            for m in re.finditer(pat, text, re.I):
                log_hits.append({"log": log.name, "line": text[:m.start()].count("\n") + 1,
                                 "text": m.group(0).strip()[:300]})
    signature = "UNCLASSIFIED"
    family = "UNKNOWN"
    if any("DRT-0073" in h["text"] for h in log_hits):
        signature, family = "DRT-0073 No access point", "PIN_ACCESS"
    elif (any("not found in library" in h["text"].lower() for h in log_hits)
          or any("missing_fakeram" in h["text"].lower() for h in log_hits)):
        signature, family = "missing macro Liberty reference", "MISSING_MACRO_LIB"
    elif failed:
        signature = f"stage {failed['stage']} rc={failed['rc']}"
    return {"run_dir": str(run), "failed_stage": failed["stage"] if failed else None,
            "failed_rc": failed["rc"] if failed else None,
            "signature": signature, "family": family,
            "evidence_refs": [str(tsv), str(ev / "run.json")]
                             + [str(h["log"]) for h in log_hits[:12]],
            "log_hits": log_hits[:40],
            "source": "deterministic_parser"}


def optional_model_note(evidence: dict[str, Any]) -> dict[str, Any]:
    """Optional provider-configurable model call; returns explicit availability."""
    url = os.environ.get("SATTVA_MODEL_URL")
    if not url:
        return {"available": False, "reason": "SATTVA_MODEL_URL not configured",
                "note": None}
    try:
        import urllib.request
        model = os.environ.get("SATTVA_MODEL_NAME", "gpt-4o-mini")
        key = os.environ.get("SATTVA_MODEL_KEY", "")
        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system",
                 "content": "You are a physical-design failure analyst. Be concise and evidence-bound."},
                {"role": "user", "content": json.dumps({
                    "signature": evidence.get("signature"),
                    "failed_stage": evidence.get("failed_stage"),
                    "log_hits": evidence.get("log_hits", [])[:12]}, indent=2)},
            ],
        }).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        req = urllib.request.Request(url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        note = data["choices"][0]["message"]["content"]
        return {"available": True, "model": model, "note": note[:2000],
                "source": "model"}
    except Exception as exc:  # noqa: BLE001 - report, never fabricate
        return {"available": False, "reason": f"model call failed: {exc}", "note": None}


def propose_patch(diagnosis: dict[str, Any], target: str | Path) -> dict[str, Any] | None:
    """Create an exact, reviewable patch for the bounded config case only."""
    target_path = Path(target)
    if diagnosis.get("family") != "MISSING_MACRO_LIB" or not target_path.is_file():
        return None
    original = target_path.read_text(encoding="utf-8")
    # Reuse the exact non-empty declaration from the source config; append it
    # after the injected empty override so the recovery actually takes effect.
    source_decls = [ln for ln in original.splitlines()
                    if ln.startswith("export ADDITIONAL_LIBS")
                    and ln.strip().endswith(".lib")
                    and "missing_fakeram" not in ln]
    if not source_decls:
        return None
    addition = source_decls[0].strip() + "\n"
    # Remove the injected invalid declaration and restore the correct one.
    lines = [ln for ln in original.splitlines(True)
             if "missing_fakeram" not in ln]
    while lines and not lines[-1].strip():
        lines.pop()
    patched = "".join(lines).rstrip("\n") + "\n\n" \
              + "# recovery: restore macro Liberty reference\n" + addition
    diff = "".join(difflib.unified_diff(
        original.splitlines(True), patched.splitlines(True),
        fromfile=str(target_path), tofile=str(target_path), n=3))
    return {"candidate_id": "RESTORE_MACRO_LIB",
            "target_file": str(target_path),
            "mechanism": "restore the pinned platform Liberty reference missing from the attempt-local config",
            "patch": diff,
            "patch_sha256": sha256_text(diff),
            "original_sha256": sha256_text(original),
            "expected_effect": "synthesis and downstream stages can resolve the macro Liberty reference",
            "risks": ["timing/congestion may change after the macro model is restored"],
            "affected_stages": ["synth", "floorplan", "place", "cts", "route", "finish"],
            "verification_criteria": [
                "baseline, failed attempt and recovered attempt all use isolated run dirs",
                "original DRT/other failure condition no longer present",
                "route completes and extraction/timing reports exist",
                "no protected artifact or original design input changed",
                "independent artifact/report review recorded"],
            "approval_status": "PENDING",
            "source": "deterministic_evidence_rule"}


def build_parser() -> Any:
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("classify")
    c.add_argument("--run", required=True)
    c.add_argument("--out")
    q = sub.add_parser("propose")
    q.add_argument("--diagnosis", required=True)
    q.add_argument("--target", required=True)
    q.add_argument("--out")
    return p


def main() -> int:
    import argparse
    args = build_parser().parse_args()
    if args.command == "classify":
        out = classify_failure(args.run)
        out["model"] = optional_model_note(out)
    else:
        diag = json.loads(Path(args.diagnosis).read_text(encoding="utf-8"))
        out = propose_patch(diag, args.target)
        if out is None:
            print(json.dumps({"status": "NO_PROPOSAL", "reason": "no bounded rule applies"},
                             indent=2))
            return 1
    if getattr(args, "out", None):
        Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                                  encoding="utf-8")
    print(json.dumps({"status": "PASS", **out} if args.command == "classify" else out,
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
