#!/usr/bin/env python3
"""Build a frozen, ground-truth-free diagnosis evidence bundle for T1.

The bundle is assembled from real T-PNR-001 failure evidence. It deliberately
excludes proposals, patches, approvals, comparison.json, recovered/baseline
runs, and any record of the verified correction or recovery outcome.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "experiments" / "T1-LIVE-DIAG" / "T-PNR-001" / "v1"

GT_DENY_TOKENS = (
    "RESTORE_MACRO_LIB", "AP-PNR-001", "AP-PNR-002", "AP-PNR-003",
    "3205f326", "8a7178f6", "recovery.patch", "proposal.json",
    "comparison.json", "orfs_baseline_recovered", "overall_rc=0",
    "first_failed_stage=null", "rerun_scope", "approved", "approval",
    "recovery outcome", "clean DRC", "rc=0",
)
GT_TOKENS_MODEL_INPUT = ("RESTORE_MACRO_LIB", "AP-PNR", "proposal.json",
                         "recovery.patch", "comparison.json",
                         "orfs_baseline_recovered")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _excerpt(path: Path, needles: tuple[str, ...], max_lines: int = 8) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    hits = [i for i, ln in enumerate(lines) if any(n in ln for n in needles)]
    start = max(0, min(hits) - 1) if hits else 0
    end = min(len(lines), max(hits) + 2) if hits else min(len(lines), max_lines)
    excerpt = "\n".join(lines[start:end]).strip()
    return {"source_path": str(path.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "line_start": start + 1, "line_end": end, "text": excerpt,
            "excerpt_sha256": sha256_text(excerpt)}


def _raw_excerpt(path: Path, line_number: int, count: int = 1) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    excerpt = "\n".join(lines[line_number - 1:line_number - 1 + count]).strip()
    return {"source_path": str(path.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "line_start": line_number, "line_end": line_number + count - 1,
            "text": excerpt, "excerpt_sha256": sha256_text(excerpt)}


def build_bundle(out: Path = DEFAULT_OUT) -> dict[str, Any]:
    attempt = ROOT / "experiments" / "PNR-RECOVERY" / "missing_macro_lib_20261125T145821Z"
    run = ROOT / "runs" / "orfs_baseline_failure_20261125T145821Z_20261125T145821234238490Z_20208"
    if not run.is_dir() or not attempt.is_dir():
        raise SystemExit("T-PNR-001 failure evidence not found")
    failed_cfg = attempt / "design" / ".config.mk.029d74562dca.bak"
    if not failed_cfg.is_file():
        raise SystemExit("failed config snapshot not found")

    entries = [
        {"id": "E01", "purpose": "failure rc and first failed stage",
         **_excerpt(run / "evidence" / "run.json", ('"overall_rc"', '"first_failed_stage"'))},
        {"id": "E02", "purpose": "stage return codes",
         **_raw_excerpt(run / "evidence" / "stages.tsv", 1, 4)},
        {"id": "E03", "purpose": "exact make failure line",
         **_raw_excerpt(run / "evidence" / "stage_synth.log", 2)},
        {"id": "E04", "purpose": "attempt-local configuration failure lines",
         **_raw_excerpt(failed_cfg, 29, 4)},
        {"id": "E05", "purpose": "earlier macro-lib declaration in the same failed config",
         **_raw_excerpt(failed_cfg, 17, 1)},
        {"id": "E06", "purpose": "declared flow stage order",
         **_excerpt(ROOT / "scripts" / "run_baseline_orfs.sh", ("STAGES=(",), 1)},
    ]
    # E04/E05 source path must be neutral in the model-visible bundle.
    for e in entries:
        if e["id"] in ("E04", "E05"):
            e["source_path"] = "design/config.mk (failed-state snapshot)"

    bundle = {"bundle_id": "T-PNR-001-v1", "schema_version": "t1_evidence_bundle/v1",
              "failure_attempt_id": run.name, "benchmark": "nangate_macro_control",
              "entries": entries}
    bundle["bundle_sha256"] = sha256_text(json.dumps(bundle, sort_keys=True))

    prompt = (
        "You are a physical-design failure analyst. Diagnose the failure using ONLY the "
        "evidence below. Return strict JSON with fields: failure_class, failed_stage, "
        "primary_hypothesis, supporting_evidence, contradicting_evidence, "
        "alternative_hypotheses, confidence, proposed_action, patch_candidate, "
        "expected_effect, affected_stages, risk_assessment, verification_plan, "
        "missing_information. Every evidence reference must use an E01..E06 id with a "
        "verbatim excerpt. If information is absent, say UNKNOWN. Do not propose executing "
        "anything or applying a patch."
    )
    rendered = prompt + "\n\n" + "\n\n".join(
        f"[{e['id']}] {e['purpose']}\n{e['text']}" for e in entries
    )
    for token in GT_TOKENS_MODEL_INPUT:
        if token.lower() in rendered.lower():
            raise SystemExit(f"ground-truth leak in prompt: {token}")

    out.mkdir(parents=True, exist_ok=True)
    (out / "bundle.json").write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n",
                                     encoding="utf-8")
    prompt_text = rendered + "\n"
    (out / "prompt.txt").write_text(prompt_text, encoding="utf-8")
    (out / "prompt_meta.json").write_text(json.dumps(
        {"prompt_version": "t1_diag_prompt/v1", "prompt_sha256": sha256_text(prompt_text),
         "bundle_sha256": bundle["bundle_sha256"]}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")

    gt = {"failure_attempt_id": run.name, "failed_stage": "synth",
          "failure_signature": "missing macro Liberty reference",
          "known_correction": "restore export ADDITIONAL_LIBS = $(PLATFORM_DIR)/lib/fakeram45_64x32.lib in the attempt-local config",
          "candidate_id": "RESTORE_MACRO_LIB",
          "affected_stages": ["synth", "floorplan", "place", "cts", "route", "finish"],
          "verified_recovery": "orfs_baseline_recovered_final_20261125T152826305943439Z_27610 rc=0, clean DRC/timing",
          "gt_sha256": ""}
    gt["gt_sha256"] = sha256_text(json.dumps(gt, sort_keys=True))
    gt_path = out / "gt.json"
    gt_path.write_text(json.dumps(gt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    gt_path.chmod(0o600)
    return {"status": "PASS", "bundle": str(out / "bundle.json"),
            "bundle_sha256": bundle["bundle_sha256"],
            "prompt_sha256": sha256_text(prompt_text), "gt_sha256": gt["gt_sha256"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    print(json.dumps(build_bundle(Path(args.out)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
