#!/usr/bin/env python3
"""Single-entry CLI for the SattvaRoute baseline/recovery workflow.

Deterministic orchestration only. Model-generated narrative is optional and
labelled. Human approval is created and validated through scripts/sattva_approval.py;
this CLI never manufactures an approval record.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTROL = ROOT / "benchmark" / "design" / "nangate_macro_control"
ATTEMPTS = ROOT / "experiments" / "PNR-RECOVERY"
RUNNER = ROOT / "scripts" / "run_baseline_orfs.sh"
APPROVAL = ROOT / "scripts" / "sattva_approval.py"
POLICY = ROOT / "state" / "approval_policy.json"
MANIFEST = ROOT / "config" / "sattva_manifest.json"


def _out(obj: Any) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True))


def _stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def cmd_status(_args: argparse.Namespace) -> int:
    digest = subprocess.run(
        ["python3", str(ROOT / "scripts" / "manifest.py"), "--manifest",
         str(MANIFEST), "--check"], capture_output=True, text=True).stdout
    _out({"status": "PASS", "manifest": json.loads(digest),
          "control_benchmark": str(CONTROL),
          "approval_gate": "human approval required for any recovery patch"})
    return 0


def _run_runner(design: Path, tag: str, env_extra: dict[str, str] | None = None,
                profile: str = "nangate_macro_control") -> dict[str, Any]:
    env = os.environ.copy()
    env.update({"SATTVA_ROOT": str(ROOT), "SATTVA_DESIGN": str(design),
                "SATTVA_DESIGN_PROFILE": profile, "RUN_TAG": tag})
    env.update(env_extra or {})
    proc = subprocess.run(["bash", str(RUNNER)], cwd=str(ROOT), env=env,
                          capture_output=True, text=True)
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("RUN_DIR=")]
    return {"rc": proc.returncode,
            "run_dir": lines[-1].split("=", 1)[1] if lines else None,
            "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}


def cmd_baseline(args: argparse.Namespace) -> int:
    out = _run_runner(CONTROL, args.tag or f"control_{_stamp()}")
    _out({"status": "PASS" if out["rc"] == 0 else "FAIL",
          "engineering_verdict": "NOT EVALUATED - inspect reports", **out})
    return 0 if out["rc"] == 0 else 1


def cmd_failure_demo(args: argparse.Namespace) -> int:
    """Create an attempt-local config with one omitted macro Liberty reference."""
    attempt = ATTEMPTS / f"missing_macro_lib_{_stamp()}"
    design = attempt / "design"
    design.mkdir(parents=True, exist_ok=False)
    base = CONTROL / "config.mk"
    text = base.read_text(encoding="utf-8")
    header = ("# Controlled failure fixture (T-PNR-001). Attempt-local only.\n"
              "# Original control config is untouched; this file deliberately\n"
              "# omits the macro Liberty reference.\n")
    fixture = header + text + "\n# injected failure: macro Liberty reference points to a missing file\n" \
                            "export ADDITIONAL_LIBS = $(DESIGN_DIR)/lib/missing_fakeram45_64x32.lib\n"
    # Copy only the readonly control collateral needed by the attempt-local
    # config; originals remain unchanged.
    import shutil
    for rel in ("rtl", "constraint.sdc", "constraint_1ns.sdc", "netlist"):
        src = CONTROL / rel
        dst = design / rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copy2(src, dst)
    target = design / "config.mk"
    target.write_text(fixture, encoding="utf-8")
    out = _run_runner(design, args.tag or f"failure_{_stamp()}")
    _out({"status": "PASS" if out["rc"] != 0 else "UNEXPECTED_PASS",
          "fixture_dir": str(attempt), "target_file": str(target),
          "injection": "export ADDITIONAL_LIBS = (attempt-local config only)",
          "approval_status": "NOT REQUESTED - failure fixture declared by implementation task",
          **out})
    return 0 if out["rc"] != 0 else 1


def cmd_diagnose(args: argparse.Namespace) -> int:
    from diagnosis_agent import classify_failure, optional_model_note
    diag = classify_failure(args.run)
    diag["model"] = optional_model_note(diag)
    if args.out:
        Path(args.out).write_text(json.dumps(diag, indent=2, sort_keys=True) + "\n",
                                  encoding="utf-8")
    _out(diag)
    return 0


def cmd_live_diagnose(args: argparse.Namespace) -> int:
    """Advisory-only live model call; never applies or approves anything."""
    import live_diagnosis as ld
    from evaluate_diagnosis import grade
    bundle_dir = Path(args.bundle)
    bundle = json.loads((bundle_dir / "bundle.json").read_text(encoding="utf-8"))
    prompt = (bundle_dir / "prompt.txt").read_text(encoding="utf-8")
    call = ld.call_model(prompt, bundle, raw_out=args.raw_out)
    result = {"status": "PASS" if call["status"] == "OK" else "BLOCKED",
              "execution_kind": call["execution_kind"],
              "provider_status": call["status"],
              "model_id": call["model_id"], "config_sha256": call["config_sha256"],
              "prompt_sha256": call["prompt_sha256"],
              "bundle_sha256": call["bundle_sha256"],
              "latency_ms": call["latency_ms"], "retries": call["retries"],
              "token_usage": call["token_usage"], "errors": call["errors"],
              "note": "advisory only; no patch application, approval, or execution"}
    if args.out:
        Path(args.out).write_text(json.dumps({"call": call}, indent=2,
                                             sort_keys=True) + "\n", encoding="utf-8")
    if call["status"] == "OK" and args.gt:
        gt = json.loads(Path(args.gt).read_text(encoding="utf-8"))
        result["evaluation"] = grade(call["parsed_output"], bundle, gt)
    _out(result)
    return 0 if call["status"] in ("OK", "SKIPPED_NO_CREDENTIALS") else 1


def cmd_propose(args: argparse.Namespace) -> int:
    import diagnosis_agent as da
    diag = json.loads(Path(args.diagnosis).read_text(encoding="utf-8"))
    proposal = da.propose_patch(diag, args.target, baseline=args.baseline,
                                mirror=args.mirror)
    if proposal is None:
        _out({"status": "NO_PROPOSAL", "reason": "no bounded rule applies"})
        return 1
    if proposal["status"] != da.INSUFFICIENT and proposal.get("status") != "insufficient_evidence":
        proposal["approval_status"] = "PENDING_HUMAN"
    if args.out:
        Path(args.out).write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n",
                                  encoding="utf-8")
    _out(proposal)
    return 0


def cmd_approve_view(args: argparse.Namespace) -> int:
    proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    print("=== RECOVERY PROPOSAL (PENDING - nothing applied) ===")
    print(f"status:       {proposal.get('status','proposal')}")
    print(f"failure:      {proposal.get('mechanism', proposal.get('family',''))}")
    print(f"target:       {proposal.get('target_file','')}")
    print(f"variable:     {proposal.get('variable','')}")
    print(f"candidate:    {proposal.get('candidate_id','')}")
    print(f"current:      {proposal.get('current_resolved_value','')}")
    print(f"intended:     {proposal.get('intended_value','')}")
    print(f"intended->:   {proposal.get('intended_value_resolved','')}")
    print(f"orig sha256:  {proposal.get('target_original_hash', proposal.get('original_sha256',''))}")
    print(f"patch sha256: {proposal.get('patch_sha256','')}")
    print(f"earliest:     {proposal.get('earliest_affected_stage','')}")
    print(f"downstream:   {', '.join(proposal.get('downstream_invalidation') or proposal.get('affected_stages') or [])}")
    print("--- exact diff ---")
    print(proposal.get("exact_diff") or proposal.get("patch") or "(none)")
    print("--- expected effect / risks ---")
    print(proposal.get("expected_effect", proposal.get("mechanism","")))
    for risk in proposal.get("risks") or []:
        print(f"  RISK: {risk}")
    print("--- verification criteria ---")
    for c in proposal.get("verification_criteria") or []:
        print(f"  - {c}")
    print("--- approval status ---")
    print(proposal.get("approval_status", "PENDING"))
    print("note: " + proposal.get("note", "textual correction for review; not applied"))
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    """Apply through the existing approval service and rerun affected stages."""
    check = subprocess.run(
        ["python3", str(APPROVAL), "validate", "--approval", args.approval,
         "--patch", args.patch, "--policy", str(POLICY), "--design-root", args.design_root,
         "--run-id", args.source_run_id, "--decision-id", args.decision_id],
        capture_output=True, text=True)
    if check.returncode != 0:
        _out({"status": "FAIL", "reason": "approval validation failed",
              "stderr": check.stderr[-1000:]})
        return 1
    approval = json.loads(Path(args.approval).read_text(encoding="utf-8"))
    out = _run_runner(Path(args.design_root), args.tag or f"recovered_{_stamp()}", {
        "SATTVA_APPROVAL": args.approval, "SATTVA_PATCH": args.patch,
        "SATTVA_POLICY": str(POLICY), "SATTVA_SOURCE_RUN": args.source_run,
        "SATTVA_SOURCE_RUN_ID": args.source_run_id,
        "SATTVA_DECISION_ID": args.decision_id,
    })
    _out({"status": "PASS" if out["rc"] == 0 else "FAIL",
          "approval_id": approval.get("approval_id"), **out})
    return 0 if out["rc"] == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    b = sub.add_parser("baseline")
    b.add_argument("--tag")
    b.set_defaults(func=cmd_baseline)
    f = sub.add_parser("failure-demo")
    f.add_argument("--tag")
    f.set_defaults(func=cmd_failure_demo)
    d = sub.add_parser("diagnose")
    d.add_argument("--run", required=True)
    d.add_argument("--out")
    d.set_defaults(func=cmd_diagnose)
    lv = sub.add_parser("live-diagnose")
    lv.add_argument("--bundle", required=True)
    lv.add_argument("--gt")
    lv.add_argument("--raw-out")
    lv.add_argument("--out")
    lv.set_defaults(func=cmd_live_diagnose)
    q = sub.add_parser("propose")
    q.add_argument("--diagnosis", required=True)
    q.add_argument("--target", required=True)
    q.add_argument("--baseline")
    q.add_argument("--mirror")
    q.add_argument("--out")
    q.set_defaults(func=cmd_propose)
    a = sub.add_parser("approve-view")
    a.add_argument("--proposal", required=True)
    a.set_defaults(func=cmd_approve_view)
    r = sub.add_parser("resume")
    for name in ("approval", "patch", "design-root", "source-run",
                 "source-run-id", "decision-id"):
        r.add_argument(f"--{name}", required=True)
    r.add_argument("--tag")
    r.set_defaults(func=cmd_resume)
    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
