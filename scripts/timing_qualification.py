#!/usr/bin/env python3
"""Produce a read-only, run-bound timing qualification record.

The adapter executes ``scripts/audit_timing.tcl`` against the saved artifacts
of a completed ORFS run (``6_final.odb`` / ``6_final.sdc`` / ``6_final.spef``)
with the pinned Liberty and RC inputs. It never invokes a flow stage and never
writes to a design input; the only files it creates are the qualification JSON
and its sibling raw tool-output file.

Missing evidence, a missing/uninvokable timing-update capability or a missing
metric is always UNKNOWN, never PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TCL = ROOT / "scripts" / "audit_timing.tcl"
DEFAULT_MANIFEST = ROOT / "config" / "sattva_manifest.json"
SCHEMA = "timing_qualification/v1"
UNKNOWN = "UNKNOWN"

import manifest as mf  # noqa: E402
import timing_audit as ta  # noqa: E402

STD_LIB = "NangateOpenCellLibrary_typical.lib"
CAPABILITY_ID = ta.CAPABILITY_ID
CAPABILITY_INVOCATION = ta.CAPABILITY_INVOCATION
WNX_RE = re.compile(r"^\s*wns\s+max\s+(-?[0-9.]+(?:[eE][+-]?\d+)?)", re.M)
TNX_RE = re.compile(r"^\s*tns\s+max\s+(-?[0-9.]+(?:[eE][+-]?\d+)?)", re.M)
VERSION_RE = re.compile(r"^OpenROAD\s+(\S+)", re.M)
METRICS = ("wns", "tns", "worst_slack_max", "worst_slack_min", "clock_period",
           "timing_paths", "unconstrained_paths", "unannotated_drivers",
           "partially_unannotated_drivers")


def sha256(path: Path) -> str:
    """Hash a file, reporting UNKNOWN rather than silently passing when absent."""
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return UNKNOWN


def finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def git(*args: str) -> str | None:
    try:
        proc = subprocess.run(["git", *args], capture_output=True, text=True,
                              timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    value = (proc.stdout or "").strip()
    return value or None if proc.returncode == 0 else None


def resolve_mirror(manifest_path: Path, args: argparse.Namespace) -> Path:
    if args.mirror:
        return Path(args.mirror).resolve()
    env_mirror = os.environ.get("SATTVA_MIRROR")
    if env_mirror:
        return Path(env_mirror).resolve()
    data = mf.load(manifest_path)
    orfs = data.get("orfs") or {}
    env_name = orfs.get("root_env")
    value = os.environ.get(env_name) if env_name else None
    return mf.resolve(value or orfs.get("root_default", "tools/OpenROAD-flow-scripts"),
                      ROOT)


def resolve_design_root(manifest_path: Path, profile: str,
                        override: str | None) -> Path | None:
    """Resolve the design root used for the canonical profile fingerprint.

    The runner passes an attempt-local ``--design-root "$DESIGN"`` to the
    manifest helper; qualifications must do the same or they bind a different
    design than the run evidence. When not supplied, use the active profile's
    declared ``design_root`` from the manifest.
    """
    if override:
        return Path(override).resolve()
    if profile == UNKNOWN:
        return None
    try:
        prof = mf.profile(mf.load(manifest_path), profile)
    except (KeyError, ValueError, OSError):
        return None
    declared = prof.get("design_root")
    return mf.resolve(declared, ROOT) if declared else None


def opensta_revision(mirror: Path) -> str:
    """Recover an OpenSTA gitlink when a checkout exposes one, else UNKNOWN."""
    declared = os.environ.get("OPENSTA_REVISION")
    if declared and re.fullmatch(r"[0-9a-fA-F]{40}", declared.strip()):
        return declared.strip().lower()
    orfs_root = mirror / "tools" / "OpenROAD"
    if (orfs_root / ".git").exists():
        for name in ("third_party/sta", "third_party/OpenSTA", "sta"):
            rev = git("-C", str(orfs_root), "rev-parse", f"HEAD:{name}")
            if rev and re.fullmatch(r"[0-9a-fA-F]{40}", rev):
                return rev.lower()
        status = git("-C", str(orfs_root), "submodule", "status") or ""
        for line in status.splitlines():
            if "opensta" in line.lower():
                rev = line.lstrip("-+ ").split()[0]
                if re.fullmatch(r"[0-9a-fA-F]{40}", rev):
                    return rev.lower()
    return UNKNOWN


def metric_from(raw: str, section_ok: set[str], section: str,
                regex: re.Pattern[str]) -> float | None:
    if section not in section_ok:
        return None
    match = regex.search(ta.section(raw, section))
    return finite(match.group(1)) if match else None


def normalized_metrics(raw: str, parsed: dict[str, Any]) -> dict[str, float | int | None]:
    section_ok = set(parsed["section_ok"])
    slack = parsed.get("slack") or {}
    clock = parsed.get("clock") or {}
    coverage = parsed.get("coverage") or {}
    parasitics = parsed.get("parasitics") or {}
    checks_max = ta.section(raw, "CHECKS_MAX") if "CHECKS_MAX" in section_ok else ""
    timing_paths = len(re.findall(r"^\s*Startpoint:\s+\S", checks_max, re.M)) or None
    return {
        "wns": metric_from(raw, section_ok, "WNS_TNS", WNX_RE),
        "tns": metric_from(raw, section_ok, "WNS_TNS", TNX_RE),
        "worst_slack_max": finite(slack.get("max")),
        "worst_slack_min": finite(slack.get("min")),
        "clock_period": finite(clock.get("period")),
        "timing_paths": timing_paths,
        "unconstrained_paths": coverage.get("unconstrained_endpoints"),
        "unannotated_drivers": parasitics.get("unannotated_drivers"),
        "partially_unannotated_drivers": parasitics.get(
            "partially_unannotated_drivers"),
    }


def capability_block(parsed: dict[str, Any]) -> dict[str, Any]:
    declared = parsed.get("capability") or {}
    status = declared.get("status") if declared.get("status") in (
        "AVAILABLE", "UNAVAILABLE") else "UNKNOWN"
    return {
        "id": CAPABILITY_ID,
        "invocation": CAPABILITY_INVOCATION,
        "available": status == "AVAILABLE",
        "rc": declared.get("rc") if status != "UNKNOWN" else None,
        "status": status,
    }


def qualification_status(parsed: dict[str, Any], metrics: dict[str, Any],
                         capability: dict[str, Any], returncode: int) -> str:
    if (returncode != 0 or not parsed.get("audit_complete")
            or parsed.get("section_errors") or capability["status"] != "AVAILABLE"):
        return "UNKNOWN"
    for name in METRICS:
        value = metrics.get(name)
        if value is None:
            return "UNKNOWN"
        if isinstance(value, float) and not math.isfinite(value):
            return "UNKNOWN"
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "UNKNOWN"
    if (metrics["wns"] < 0 or metrics["tns"] < 0
            or metrics["worst_slack_max"] < 0 or metrics["worst_slack_min"] < 0
            or metrics["unconstrained_paths"] > 0
            or metrics["unannotated_drivers"] > 0
            or metrics["partially_unannotated_drivers"] > 0
            or metrics["timing_paths"] < 1):
        return "FAIL"
    return "PASS"


def build_record(*, run: Path, results: Path, platform: Path, macro_lib: str,
                 profile: str, manifest_path: Path, mirror: Path,
                 design_root: Path | None, raw: str,
                 raw_path: Path, exe: str, argv: list[str], returncode: int,
                 parsed: dict[str, Any]) -> dict[str, Any]:
    run_json = run / "evidence" / "run.json"
    run_id = UNKNOWN
    if run_json.is_file():
        try:
            run_id = json.loads(run_json.read_text(encoding="utf-8")).get("run_id") or UNKNOWN
        except (ValueError, OSError):
            pass

    # Bind to the fingerprint recorded by this run's own evidence. The design
    # root is mutable (an approved patch can change config.mk after evidence
    # capture), so recomputing from it would bind a different design than the
    # verifier compares against. --design-root remains accepted for provenance
    # only; a missing recorded fingerprint fails closed as UNKNOWN.
    fingerprint = UNKNOWN
    ev_manifest = run / "evidence" / "manifest.json"
    try:
        if ev_manifest.is_file():
            recorded = json.loads(ev_manifest.read_text(encoding="utf-8")).get("fingerprint")
            if isinstance(recorded, str) and recorded.strip():
                fingerprint = recorded.strip()
    except (ValueError, OSError):
        pass
    orfs_rev = git("-C", str(mirror), "rev-parse", "HEAD") or UNKNOWN

    version_m = VERSION_RE.search(raw)
    exe_path = Path(exe)
    tool = {
        "id": "openroad",
        "version": version_m.group(1) if version_m else UNKNOWN,
        "exe_sha256": sha256(exe_path),
        "invocation": shlex.join(argv),
    }
    binding = {
        "design_fingerprint": fingerprint,
        "orfs_revision": orfs_rev,
        "opensta_revision": opensta_revision(mirror),
        "sdc_sha256": sha256(results / "6_final.sdc"),
        "liberty_std_sha256": sha256(platform / "lib" / STD_LIB),
        "liberty_macro_sha256": sha256(platform / "lib" / macro_lib),
        "rc_set_sha256": sha256(platform / "setRC.tcl"),
        "rcx_rules_sha256": sha256(platform / "rcx_patterns.rules"),
        "spef_sha256": sha256(results / "6_final.spef"),
        "odb_sha256": sha256(results / "6_final.odb"),
        "tool": tool,
        "raw_output_sha256": sha256(raw_path),
    }
    capability = capability_block(parsed)
    metrics = normalized_metrics(raw, parsed)
    status = qualification_status(parsed, metrics, capability, returncode)
    if (returncode != 0 or not parsed.get("audit_complete")
            or parsed.get("section_errors")
            or profile == UNKNOWN or fingerprint == UNKNOWN):
        status = "UNKNOWN"
    return {
        "schema": SCHEMA,
        "run_id": run_id,
        "active_profile": profile,
        "binding": binding,
        "capability": capability,
        "metrics": metrics,
        "status": status,
        "raw_output": str(raw_path),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--platform", required=True)
    p.add_argument("--macro-lib", required=True)
    p.add_argument("--out", help="qualification JSON path (default: <out-dir>/<prefix>_qualification.json)")
    p.add_argument("--prefix", help="evidence prefix used when --out is not given")
    p.add_argument("--out-dir", default=str(ROOT / "evidence" / "timing"))
    p.add_argument("--openroad", default=os.environ.get("OPENROAD_EXE", "openroad"))
    p.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    p.add_argument("--mirror", default=None)
    p.add_argument("--profile", default=os.environ.get("SATTVA_DESIGN_PROFILE", UNKNOWN))
    p.add_argument("--design-root", default=None,
                   help="design root for the canonical fingerprint (default: profile design_root)")
    args = p.parse_args()

    if not args.out and not args.prefix:
        p.error("one of --out or --prefix is required")
    run = Path(args.run).resolve()
    platform = Path(args.platform).resolve()
    manifest_path = Path(args.manifest).resolve()
    out = Path(args.out).resolve() if args.out else (
        Path(args.out_dir).resolve() / f"{args.prefix}_qualification.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    raw_path = out.with_suffix(".raw.txt")

    results = ta.find_results(run)
    mirror = resolve_mirror(manifest_path, args)
    design_root = resolve_design_root(manifest_path, args.profile, args.design_root)
    exe = shutil.which(args.openroad) or args.openroad
    env = dict(os.environ)
    env.update(AUDIT_RESULTS=str(results), AUDIT_PLATFORM=str(platform),
               AUDIT_MACRO_LIB=args.macro_lib)
    argv = [exe, "-no_init", "-exit", str(TCL)]
    try:
        proc = subprocess.run(argv, env=env, capture_output=True, text=True,
                              timeout=1800)
        raw = proc.stdout + proc.stderr
        returncode = proc.returncode
    except (OSError, subprocess.SubprocessError) as exc:
        raw = f"OPENROAD_INVOCATION_ERROR {exc}\n"
        returncode = 127
    raw_path.write_text(raw, encoding="utf-8")

    parsed = ta.parse(raw)
    record = build_record(run=run, results=results, platform=platform,
                          macro_lib=args.macro_lib, profile=args.profile,
                          manifest_path=manifest_path, mirror=mirror,
                          design_root=design_root, raw=raw,
                          raw_path=raw_path, exe=exe, argv=argv,
                          returncode=returncode, parsed=parsed)
    out.write_text(json.dumps(record, indent=2, sort_keys=True,
                              allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"schema": record["schema"], "run_id": record["run_id"],
                      "status": record["status"], "out": str(out),
                      "raw_output": record["raw_output"]},
                     indent=2, sort_keys=True))
    return 0 if record["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
