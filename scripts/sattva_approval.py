#!/usr/bin/env python3
"""SattvaRoute exact-patch approval enforcement (FDE-002).

Standard library only. No database, framework, network or hosted-model access.

This module is the deterministic control boundary for recovery operations:
  * approval records are machine-readable JSON bound to an exact patch;
  * validate() rejects every unauthorized/stale/altered/ambiguous case;
  * apply_patch() mutates exactly one permitted target, atomically, with backup
    and rollback evidence;
  * rerun scope is validated against an explicit policy derived from the
    observed ORFS stage inputs, never guessed.

It does not run EDA and does not decide whether a fix is physically correct.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

REQUIRED_FIELDS = (
    "approval_id", "decision_id", "source_run_id", "input_fingerprint",
    "patch_sha256", "target_file", "expected_original_hash",
    "earliest_affected_stage", "rerun_scope", "status", "approver",
    "timestamp",
)
OPTIONAL_FIELDS = ("note",)
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


class ApprovalError(Exception):
    """Raised for any rejected approval or unsafe patch operation."""


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ApprovalError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ApprovalError(f"approval/policy root must be a JSON object: {path}")
    return data


def atomic_write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def operation_id(approval: dict) -> str:
    """Stable identity of the approved operation (excludes approver note/time)."""
    keys = ("approval_id", "decision_id", "source_run_id", "patch_sha256",
            "target_file", "earliest_affected_stage", "rerun_scope")
    payload = {k: approval.get(k) for k in keys}
    return sha256_bytes(json.dumps(payload, sort_keys=True).encode("utf-8"))


def load_policy(path: Path) -> dict:
    policy = load_json(path)
    for key in ("allowed_roots", "stages", "stage_inputs", "input_files", "ledger"):
        if key not in policy:
            raise ApprovalError(f"policy missing required key: {key}")
    return policy


def compute_input_fingerprint(design_root: Path, policy: dict) -> str:
    """Fingerprint the design inputs named by policy (relative to design_root)."""
    items = []
    for rel in policy["input_files"]:
        p = design_root / rel
        if not p.is_file():
            raise ApprovalError(f"input file missing for fingerprint: {p}")
        items.append(f"{rel}\0{sha256_file(p)}")
    return sha256_bytes("\0".join(items).encode("utf-8"))


def check_path_safety(target: Path, policy: dict) -> None:
    """Reject traversal, absolute escapes and symlinks in any path component."""
    if not target.is_absolute():
        raise ApprovalError(f"target must be absolute: {target}")
    parts = target.parts
    if ".." in parts:
        raise ApprovalError(f"path traversal rejected: {target}")
    for parent in (target.parent, *target.parent.parents):
        if parent.is_symlink():
            raise ApprovalError(f"symlink component rejected: {parent}")
    if target.is_symlink():
        raise ApprovalError(f"target itself is a symlink: {target}")
    allowed = [Path(p).resolve() for p in policy["allowed_roots"]]
    resolved = target.resolve()
    if not any(resolved == root or root in resolved.parents for root in allowed):
        raise ApprovalError(f"target outside permitted boundary: {target}")


def validate_scope(approval: dict, policy: dict) -> list[str]:
    scope = approval.get("rerun_scope")
    if not isinstance(scope, list) or not scope or not all(isinstance(s, str) for s in scope):
        raise ApprovalError("rerun_scope must be a non-empty list of stage names")
    stages = policy["stages"]
    if len(set(scope)) != len(scope):
        raise ApprovalError("rerun_scope contains duplicates")
    unknown = [s for s in scope if s not in stages]
    if unknown:
        raise ApprovalError(f"rerun_scope contains unknown stages: {unknown}")
    if scope != stages[stages.index(scope[0]):stages.index(scope[0]) + len(scope)]:
        raise ApprovalError("rerun_scope must be contiguous in stage order")
    earliest = approval.get("earliest_affected_stage")
    if earliest not in stages:
        raise ApprovalError(f"earliest_affected_stage is not a known stage: {earliest}")
    if scope[0] != earliest:
        raise ApprovalError("rerun_scope must start at the earliest affected stage")
    return scope


def check_ledger(ledger: Path, approval_id: str, op_id: str, *, for_apply: bool) -> None:
    if not ledger.exists():
        return
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise ApprovalError(f"corrupt approval ledger: {exc}") from exc
        if row.get("approval_id") != approval_id:
            continue
        if row.get("operation_id") != op_id:
            raise ApprovalError("approval already consumed by a different operation")
        if for_apply:
            raise ApprovalError("approval already consumed (reuse rejected)")


def validate_approval(approval: dict, patch_path: Path, policy: dict,
                      design_root: Path, *, run_id: str, decision_id: str | None,
                      for_apply: bool = False, expected_target_hash: str | None = None) -> dict:
    """Return a validation report or raise ApprovalError."""
    missing = [k for k in REQUIRED_FIELDS if k not in approval]
    if missing:
        raise ApprovalError(f"missing required approval fields: {missing}")
    unexpected = [k for k in approval if k not in REQUIRED_FIELDS + OPTIONAL_FIELDS + ("operation_id",)]
    if unexpected:
        raise ApprovalError(f"unexpected approval fields: {unexpected}")
    if approval["status"] not in ("APPROVED", "REJECTED"):
        raise ApprovalError("status must be APPROVED or REJECTED")
    if approval["status"] == "REJECTED":
        raise ApprovalError("approval status is REJECTED")
    if approval["source_run_id"] != run_id:
        raise ApprovalError(f"run id mismatch: {approval['source_run_id']} != {run_id}")
    if decision_id is not None and approval["decision_id"] != decision_id:
        raise ApprovalError("decision id mismatch")
    if not isinstance(approval["approver"], str) or not approval["approver"].strip():
        raise ApprovalError("approver is required")
    try:
        _dt.datetime.fromisoformat(approval["timestamp"])
    except (ValueError, TypeError) as exc:
        raise ApprovalError(f"invalid timestamp: {exc}") from exc

    patch_bytes = patch_path.read_bytes()
    if sha256_bytes(patch_bytes) != approval["patch_sha256"]:
        raise ApprovalError("patch SHA-256 mismatch")
    if compute_input_fingerprint(design_root, policy) != approval["input_fingerprint"]:
        raise ApprovalError("input fingerprint mismatch")

    target = Path(approval["target_file"])
    check_path_safety(target, policy)
    if not target.is_file():
        raise ApprovalError(f"target file missing: {target}")
    op_id = operation_id(approval)
    if approval.get("operation_id") not in (None, op_id):
        raise ApprovalError("operation_id field inconsistent with record contents")
    # Ledger checks precede the target-hash check so approval reuse is reported
    # precisely even when the file has already been patched.
    ledger = Path(policy["ledger"])
    check_ledger(ledger, approval["approval_id"], op_id, for_apply=for_apply)

    current_hash = sha256_file(target)
    if expected_target_hash is not None:
        if current_hash != expected_target_hash:
            raise ApprovalError("target final hash mismatch on resumed validation")
    elif current_hash != approval["expected_original_hash"]:
        raise ApprovalError("target original hash mismatch")

    scope = validate_scope(approval, policy)

    return dict(operation_id=op_id, rerun_scope=scope,
                target=str(target), patch_sha256=approval["patch_sha256"],
                input_fingerprint=approval["input_fingerprint"],
                validated_at=utc_now(), for_apply=for_apply)


def apply_unified_diff(original: str, patch: str) -> str:
    """Strictly apply a single-target unified diff; reject any mismatch."""
    src = original.splitlines(keepends=True)
    lines = patch.splitlines(keepends=True)
    out: list[str] = []
    src_i = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("--- ") or line.startswith("+++ ") or line.startswith("\\"):
            i += 1
            continue
        m = HUNK_RE.match(line)
        if not m:
            raise ApprovalError(f"unexpected patch line: {line!r}")
        old_start = int(m.group(1)) - 1
        old_count = int(m.group(2) or 1)
        new_count = int(m.group(4) or 1)
        if old_start < src_i or old_start > len(src):
            raise ApprovalError("patch hunk out of order")
        out.extend(src[src_i:old_start])
        src_i = old_start
        consumed_old = 0
        consumed_new = 0
        i += 1
        while i < len(lines):
            body = lines[i]
            if HUNK_RE.match(body) or body.startswith("--- ") or body.startswith("+++ "):
                break
            prefix, text = body[:1], body[1:]
            if prefix == " ":
                if src_i >= len(src) or src[src_i] != text:
                    raise ApprovalError("patch context mismatch")
                out.append(text)
                src_i += 1
                consumed_old += 1
                consumed_new += 1
            elif prefix == "-":
                if src_i >= len(src) or src[src_i] != text:
                    raise ApprovalError("patch removal mismatch")
                src_i += 1
                consumed_old += 1
            elif prefix == "+":
                out.append(text)
                consumed_new += 1
            elif body.strip() == "" or body.startswith("\\"):
                pass
            else:
                raise ApprovalError(f"malformed patch line: {body!r}")
            i += 1
        if consumed_old != old_count or consumed_new != new_count:
            raise ApprovalError("patch hunk line counts do not match")
    out.extend(src[src_i:])
    return "".join(out)


class TargetLock:
    """Cross-process exclusive lock with stale-PID recovery."""

    def __init__(self, target: Path):
        self.path = target.parent / f".{target.name}.sattva.lock"
        self.fd: int | None = None

    def __enter__(self):
        if self.path.exists():
            try:
                pid = int(self.path.read_text().strip())
                os.kill(pid, 0)
            except (ValueError, OSError, ProcessLookupError):
                self.path.unlink(missing_ok=True)
            else:
                raise ApprovalError(f"another application holds the target lock (pid {pid})")
        self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.write(self.fd, str(os.getpid()).encode())
        return self

    def __exit__(self, *_exc):
        if self.fd is not None:
            os.close(self.fd)
        self.path.unlink(missing_ok=True)


def apply_patch(approval: dict, patch_path: Path, policy: dict, evidence_dir: Path) -> dict:
    """Apply the approved patch atomically; write before/after + rollback evidence."""
    report = validate_approval(approval, patch_path, policy,
                               Path(policy.get("_design_root", "/")),
                               run_id=approval["source_run_id"],
                               decision_id=None, for_apply=True)
    target = Path(approval["target_file"])
    check_path_safety(target, policy)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    state_path = evidence_dir / "approval_apply.json"
    op_id = report["operation_id"]

    if state_path.exists():
        state = load_json(state_path)
        if state.get("operation_id") == op_id and state.get("phase") in ("applied", "verified"):
            final_hash = state.get("after_sha256")
            if final_hash and sha256_file(target) == final_hash:
                return dict(**state, resumed=True)
            raise ApprovalError("recorded apply state does not match target; operator resolution required")
        if state.get("operation_id") == op_id and state.get("phase") == "started":
            raise ApprovalError("interrupted apply state; operator resolution required (no implicit retry)")

    with TargetLock(target):
        original = target.read_bytes()
        current = sha256_bytes(original)
        if current != approval["expected_original_hash"]:
            raise ApprovalError("target changed concurrently before apply")
        final_text = apply_unified_diff(original.decode("utf-8"),
                                        patch_path.read_text(encoding="utf-8"))
        final_bytes = final_text.encode("utf-8")
        final_hash = sha256_bytes(final_bytes)

        backup = target.parent / f".{target.name}.{op_id[:12]}.bak"
        backup.write_bytes(original)
        record = dict(operation_id=op_id, phase="started", target=str(target),
                      before_sha256=current, after_sha256=final_hash,
                      backup=str(backup), backup_sha256=sha256_file(backup),
                      started_at=utc_now())
        atomic_write_json(state_path, record)

        fd, tmp = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(final_bytes)
                fh.flush()
                os.fsync(fh.fileno())
            os.chmod(tmp, target.stat().st_mode)
            os.replace(tmp, target)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

        if sha256_file(target) != final_hash:
            shutil.copy2(backup, target)
            record["phase"] = "rolled_back"
            record["error"] = "post-apply hash verification failed"
            atomic_write_json(state_path, record)
            raise ApprovalError("post-apply hash verification failed; original restored")

        record["phase"] = "verified"
        record["verified_at"] = utc_now()
        atomic_write_json(state_path, record)

    ledger = Path(policy["ledger"])
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(approval_id=approval["approval_id"],
                                 operation_id=op_id, target=str(target),
                                 patch_sha256=approval["patch_sha256"],
                                 timestamp=utc_now()), sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return record


def cmd_create(args) -> None:
    policy = load_policy(Path(args.policy))
    patch = Path(args.patch)
    design_root = Path(args.design_root)
    target = Path(args.target)
    check_path_safety(target, policy)
    approval = dict(
        approval_id=args.approval_id,
        decision_id=args.decision_id,
        source_run_id=args.source_run_id,
        input_fingerprint=compute_input_fingerprint(design_root, policy),
        patch_sha256=sha256_file(patch),
        target_file=str(target),
        expected_original_hash=sha256_file(target),
        earliest_affected_stage=args.earliest_stage,
        rerun_scope=[s.strip() for s in args.rerun_scope.split(",") if s.strip()],
        status=args.status,
        approver=args.approver,
        timestamp=utc_now(),
    )
    if args.note:
        approval["note"] = args.note
    validate_scope(approval, policy)
    approval["operation_id"] = operation_id(approval)
    atomic_write_json(Path(args.out), approval)
    print(f"APPROVAL_CREATED {Path(args.out)} status={approval['status']} "
          f"operation_id={approval['operation_id'][:12]}")


def cmd_validate(args) -> None:
    policy = load_policy(Path(args.policy))
    approval = load_json(Path(args.approval))
    report = validate_approval(approval, Path(args.patch), policy,
                               Path(args.design_root), run_id=args.run_id,
                               decision_id=args.decision_id,
                               for_apply=args.for_apply)
    print("APPROVAL_VALID " + json.dumps(report, sort_keys=True))


def cmd_apply(args) -> None:
    policy = load_policy(Path(args.policy))
    policy["_design_root"] = args.design_root
    approval = load_json(Path(args.approval))
    record = apply_patch(approval, Path(args.patch), policy, Path(args.evidence_dir))
    print("PATCH_APPLIED " + json.dumps(record, sort_keys=True))


def cmd_guard(args) -> None:
    """Execution-boundary gate: validate, revalidate, apply, revalidate.

    A completed apply from a previous invocation is recognized via the durable
    apply-state file; it is never applied twice. An interrupted 'started' state
    is refused and requires operator resolution.
    """
    policy = load_policy(Path(args.policy))
    policy["_design_root"] = args.design_root
    approval = load_json(Path(args.approval))
    patch = Path(args.patch)
    state_path = Path(args.evidence_dir) / "approval_apply.json"
    op_id = operation_id(approval)
    target = Path(approval["target_file"])

    resumed = False
    final_hash = None
    if state_path.exists():
        state = load_json(state_path)
        if state.get("operation_id") == op_id and state.get("phase") in ("applied", "verified"):
            if not target.is_file() or sha256_file(target) != state.get("after_sha256"):
                raise ApprovalError("previous apply state does not match target; operator resolution required")
            resumed = True
            final_hash = state["after_sha256"]
        elif state.get("operation_id") == op_id and state.get("phase") == "started":
            raise ApprovalError("interrupted apply state; operator resolution required")

    if resumed:
        first = validate_approval(approval, patch, policy, Path(args.design_root),
                                  run_id=args.run_id, decision_id=args.decision_id,
                                  for_apply=False, expected_target_hash=final_hash)
        apply_phase = "resumed"
    else:
        first = validate_approval(approval, patch, policy, Path(args.design_root),
                                  run_id=args.run_id, decision_id=args.decision_id,
                                  for_apply=True)
        second = validate_approval(approval, patch, policy, Path(args.design_root),
                                   run_id=args.run_id, decision_id=args.decision_id,
                                   for_apply=True)
        if first != second:
            raise ApprovalError("approval state changed between validation passes")
        record = apply_patch(approval, patch, policy, Path(args.evidence_dir))
        apply_phase = record["phase"]
        final_hash = record["after_sha256"]

    final = validate_approval(approval, patch, policy, Path(args.design_root),
                              run_id=args.run_id, decision_id=args.decision_id,
                              for_apply=False, expected_target_hash=final_hash)
    guard = dict(status="PASS", run_id=args.run_id, approval_id=approval["approval_id"],
                 operation_id=op_id, rerun_scope=first["rerun_scope"],
                 apply_phase=apply_phase, revalidated_at=final["validated_at"])
    atomic_write_json(Path(args.evidence_dir) / "approval_guard.json", guard)
    print("APPROVAL_GUARD_PASS " + json.dumps(guard, sort_keys=True))


def cmd_check_source_artifacts(args) -> None:
    policy = load_policy(Path(args.policy))
    approval = load_json(Path(args.approval))
    scope = validate_scope(approval, policy)
    results_root = Path(args.source_work) / "results" / "asap7" / "sattva_sram" / "base"
    missing = {}
    for stage in scope:
        needed = policy["stage_inputs"].get(stage, [])
        missing[stage] = [f for f in needed if not (results_root / f).is_file()]
    if any(missing.values()):
        raise ApprovalError(f"source artifacts missing for rerun scope: {missing}")
    print("SOURCE_ARTIFACTS_OK " + json.dumps({s: policy["stage_inputs"].get(s, []) for s in scope}))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create")
    c.add_argument("--approval-id", required=True)
    c.add_argument("--decision-id", required=True)
    c.add_argument("--source-run-id", required=True)
    c.add_argument("--patch", required=True)
    c.add_argument("--target", required=True)
    c.add_argument("--earliest-stage", required=True)
    c.add_argument("--rerun-scope", required=True)
    c.add_argument("--status", choices=("APPROVED", "REJECTED"), default="APPROVED")
    c.add_argument("--approver", required=True)
    c.add_argument("--design-root", required=True)
    c.add_argument("--policy", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--note")
    c.set_defaults(func=cmd_create)

    v = sub.add_parser("validate")
    v.add_argument("--approval", required=True)
    v.add_argument("--patch", required=True)
    v.add_argument("--policy", required=True)
    v.add_argument("--design-root", required=True)
    v.add_argument("--run-id", required=True)
    v.add_argument("--decision-id")
    v.add_argument("--for-apply", action="store_true")
    v.set_defaults(func=cmd_validate)

    a = sub.add_parser("apply")
    a.add_argument("--approval", required=True)
    a.add_argument("--patch", required=True)
    a.add_argument("--policy", required=True)
    a.add_argument("--design-root", required=True)
    a.add_argument("--evidence-dir", required=True)
    a.set_defaults(func=cmd_apply)

    g = sub.add_parser("guard")
    g.add_argument("--approval", required=True)
    g.add_argument("--patch", required=True)
    g.add_argument("--policy", required=True)
    g.add_argument("--design-root", required=True)
    g.add_argument("--run-id", required=True)
    g.add_argument("--decision-id")
    g.add_argument("--evidence-dir", required=True)
    g.set_defaults(func=cmd_guard)

    s = sub.add_parser("check-source-artifacts")
    s.add_argument("--approval", required=True)
    s.add_argument("--policy", required=True)
    s.add_argument("--source-work", required=True)
    s.set_defaults(func=cmd_check_source_artifacts)
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
    except ApprovalError as exc:
        print(f"APPROVAL_ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
