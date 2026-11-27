#!/usr/bin/env python3
"""Produce a structured timing audit for a completed ORFS run.

Runs ``scripts/audit_timing.tcl`` in the pinned OpenROAD build and records the
tool's own unit/clock/coverage view together with the Liberty declarations that
define those units. The output is the artifact ``verify_run.py`` requires before
it will interpret a timing number: without a unit and a corner, a slack value is
not evidence.

Environment: OpenROAD is invoked from PATH (use WSL for the local mirror).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TCL = ROOT / "scripts" / "audit_timing.tcl"
AUDIT_SCHEMA = "timing_audit/v2"
MANDATORY_SECTIONS = (
    "LIBERTY", "LOAD", "RC_CORNER", "SPEF", "UPDATE_TIMING",
    "REPORT_UNITS", "CLOCK_PROPERTIES", "WORST_SLACK",
    "CHECK_SETUP", "PARASITICS", "COVERAGE",
)

UNIT_RE = re.compile(r"^\s*(time|capacitance|resistance|voltage|current|power|distance)\s+(\S+)\s*$", re.M)
CLOCK_RE = re.compile(r"^(\S+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*$", re.M)
WORST_RE = re.compile(r"worst slack (max|min)\s+(-?[0-9.]+)")
PERIOD_RE = re.compile(r"period_min\s*=\s*([0-9.]+|inf)\s*fmax\s*=\s*(\S+)")
UNANNOTATED_RE = re.compile(r"Found\s+(\d+)\s+unannotated drivers")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section(text: str, name: str) -> str:
    marker = f"===== {name} ====="
    idx = text.find(marker)
    if idx < 0:
        return ""
    start = idx + len(marker)
    nxt = text.find("\n===== ", start)
    return (text[start:nxt] if nxt >= 0 else text[start:]).strip("\n")


def liberty_meta(lib: Path) -> dict[str, Any]:
    text = lib.read_text(encoding="utf-8", errors="replace")

    def one(pattern: str) -> str | None:
        m = re.search(pattern, text)
        return m.group(1) if m else None

    return {
        "path": str(lib),
        "sha256": sha256(lib),
        "time_unit": one(r'time_unit\s*:\s*"([^"]+)"'),
        "capacitance_unit": one(r'capacitance_unit\s*:\s*"([^"]+)"'),
        "voltage_unit": one(r'voltage_unit\s*:\s*"([^"]+)"'),
        "nom_voltage": one(r"nom_voltage\s*:\s*([0-9.]+)"),
        "nom_temperature": one(r"nom_temperature\s*:\s*([0-9.]+)"),
        "nom_process": one(r"nom_process\s*:\s*([0-9.]+)"),
        "default_operating_conditions": one(
            r"default_operating_conditions\s*:\s*([A-Za-z0-9_.]+)"),
    }


def find_results(run: Path) -> Path:
    hits = sorted(run.rglob("6_final.odb"))
    if not hits:
        raise SystemExit(f"no 6_final.odb under {run}")
    return hits[0].parent


def _finite(value: float | None) -> float | None:
    return value if value is not None and math.isfinite(value) else None


def parse(raw: str) -> dict[str, Any]:
    """Parse an audit stream, failing closed on missing/error sections.

    Warning text from ``check_setup -verbose`` is never treated as an endpoint
    count. The count, when available, comes from the UNCONSTRAINED report's
    Startpoint/Endpoint pairs. Missing or unsupported sections yield ``None``.
    """
    section_ok = set(re.findall(r"^SECTION_OK (\w+)\s*$", raw, re.M))
    section_errors = [{"section": m.group(1), "detail": m.group(2).strip()}
                      for m in re.finditer(r"^SECTION_ERROR (\w+):?\s*(.*)$", raw, re.M)]
    unsupported = [{"section": m.group(1), "detail": m.group(2).strip()}
                   for m in re.finditer(r"^SECTION_UNSUPPORTED (\w+):?\s*(.*)$", raw, re.M)]
    status = re.search(r"^AUDIT_STATUS (\w+) errors=(\d+)", raw, re.M)
    audit_done = "===== AUDIT_DONE =====" in raw
    mandatory_ok = all(name in section_ok for name in MANDATORY_SECTIONS)
    complete = bool(audit_done and status and status.group(1) == "OK"
                    and mandatory_ok and not section_errors)

    units = {k: v for k, v in UNIT_RE.findall(section(raw, "REPORT_UNITS"))}
    clock = None
    if "CLOCK_PROPERTIES" in section_ok:
        cm = CLOCK_RE.search(section(raw, "CLOCK_PROPERTIES"))
        if cm:
            period = _finite(float(cm.group(2)))
            waveform = [_finite(float(cm.group(3))), _finite(float(cm.group(4)))]
            if period is not None and all(v is not None for v in waveform):
                clock = {"name": cm.group(1), "period": period, "waveform": waveform}

    slack = {}
    if "WORST_SLACK" in section_ok:
        for m in WORST_RE.finditer(section(raw, "WORST_SLACK")):
            value = _finite(float(m.group(2)))
            if value is not None:
                slack[m.group(1)] = value

    def min_period(name: str) -> dict[str, Any]:
        m = PERIOD_RE.search(section(raw, name)) if name in section_ok else None
        if not m:
            return {"period_min": None, "fmax": None}
        period = None if m.group(1) == "inf" else _finite(float(m.group(1)))
        fmax = None if m.group(2) == "inf" else m.group(2)
        return {"period_min": period, "fmax": fmax}

    coverage: dict[str, Any] = {}
    if "COVERAGE" in section_ok:
        cov = section(raw, "COVERAGE")
        for key in ("input_ports", "output_ports", "register_clock_pins",
                    "registers", "clocks"):
            m = re.search(rf"^{key} (\d+)$", cov, re.M)
            coverage[key] = int(m.group(1)) if m else None
        for m in re.finditer(r"^clock (\S+) period (\S+)$", cov, re.M):
            coverage.setdefault("clock_periods", {})[m.group(1)] = (
                _finite(float(m.group(2))) if re.fullmatch(r"[0-9.]+", m.group(2)) else None)

    check_setup = section(raw, "CHECK_SETUP").strip()
    check_setup_completed = (("CHECK_SETUP_OK" in raw or "CHECK_SETUP" in section_ok)
                             and all(e["section"] != "CHECK_SETUP" for e in section_errors))
    warnings = [ln for ln in check_setup.splitlines()
                if ln.strip() and not ln.startswith(("SECTION_ERROR", "CHECK_SETUP_OK",
                                                     "SECTION_OK"))]
    # check_setup is the supported clean/ambiguous signal. A non-empty verbose
    # output means coverage is not established; its line count is NOT an
    # endpoint count. report_checks -unconstrained is retained as raw evidence
    # but is not converted into a fabricated endpoint total.
    unconstrained = 0 if check_setup_completed and not warnings else None
    un = section(raw, "UNCONSTRAINED") if "UNCONSTRAINED" in section_ok else ""
    coverage["unconstrained_endpoints"] = unconstrained
    coverage["check_setup_completed"] = check_setup_completed
    coverage["check_setup_warnings"] = warnings
    coverage["unconstrained_report_lines"] = len(
        re.findall(r"^\s*Startpoint:\s*\S+", un, re.M))

    par = section(raw, "PARASITICS") if "PARASITICS" in section_ok else ""
    parasitics = {
        "unannotated_drivers": (int(UNANNOTATED_RE.search(par).group(1))
                                if UNANNOTATED_RE.search(par) else None),
        "partially_unannotated_drivers": (int(m.group(1))
                                          if (m := re.search(
                                              r"Found\s+(\d+)\s+partially unannotated drivers", par))
                                          else None),
    }
    return {
        "schema": AUDIT_SCHEMA,
        "audit_complete": complete,
        "audit_status": status.group(1) if status else None,
        "section_ok": sorted(section_ok),
        "section_errors": section_errors,
        "unsupported_sections": unsupported,
        "units": units,
        "clock": clock,
        "slack": slack,
        "period_min": {
            "reg_to_reg": min_period("MIN_PERIOD_REG_TO_REG"),
            "including_ports": min_period("MIN_PERIOD_INCLUDING_PORTS"),
        },
        "coverage": coverage,
        "parasitics": parasitics,
        "check_setup": check_setup,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True)
    p.add_argument("--platform", required=True)
    p.add_argument("--macro-lib", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--openroad", default=os.environ.get("OPENROAD_EXE", "openroad"))
    args = p.parse_args()

    run = Path(args.run).resolve()
    platform = Path(args.platform).resolve()
    results = find_results(run)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env.update(AUDIT_RESULTS=str(results), AUDIT_PLATFORM=str(platform),
               AUDIT_MACRO_LIB=args.macro_lib)
    exe = shutil.which(args.openroad) or args.openroad
    proc = subprocess.run([exe, "-no_init", "-exit", str(TCL)],
                          env=env, capture_output=True, text=True)
    raw = proc.stdout + proc.stderr
    raw_path = out.with_suffix(".raw.txt")
    raw_path.write_text(raw, encoding="utf-8")

    parsed = parse(raw)
    run_json = run / "evidence" / "run.json"
    run_id = None
    if run_json.is_file():
        try:
            run_id = json.loads(run_json.read_text(encoding="utf-8")).get("run_id")
        except (ValueError, OSError):
            run_id = None
    ev_manifest = run / "evidence" / "manifest.json"
    fingerprint = None
    if ev_manifest.is_file():
        try:
            fingerprint = json.loads(ev_manifest.read_text(encoding="utf-8")).get("digest")
        except (ValueError, OSError):
            fingerprint = None

    def first(name: str) -> Path | None:
        hits = sorted(run.rglob(name))
        return hits[0] if hits else None

    artifacts = {}
    for name in ("6_final.odb", "6_final.sdc", "6_final.spef",
                 "6_finish.rpt", "5_route_drc.rpt"):
        path = first(name)
        artifacts[name] = {"path": str(path) if path else None,
                           "sha256": sha256(path) if path and path.is_file() else None}

    meta = {
        "schema": AUDIT_SCHEMA,
        "run": str(run),
        "results_dir": str(results),
        "binding": {
            "run_id": run_id,
            "active_profile": os.environ.get("SATTVA_DESIGN_PROFILE", "UNKNOWN"),
            "dependency_fingerprint": fingerprint,
            "tool_identity": exe,
            "tool_sha256": sha256(Path(exe)) if Path(exe).is_file() else None,
            "artifacts": artifacts,
        },
        "openroad": exe,
        "openroad_sha256": sha256(Path(exe)) if Path(exe).is_file() else None,
        "returncode": proc.returncode,
        "raw_audit": str(raw_path),
        "raw_audit_sha256": sha256(raw_path),
        "liberty": [liberty_meta(platform / "lib" / "NangateOpenCellLibrary_typical.lib"),
                    liberty_meta(platform / "lib" / args.macro_lib)],
        "rc_corner": {
            "setrc": str(platform / "setRC.tcl"),
            "setrc_sha256": (sha256(platform / "setRC.tcl")
                             if (platform / "setRC.tcl").is_file() else None),
            "rcx_rules": str(platform / "rcx_patterns.rules"),
            "rcx_rules_sha256": (sha256(platform / "rcx_patterns.rules")
                                 if (platform / "rcx_patterns.rules").is_file() else None),
        },
    }
    meta.update(parsed)
    out.write_text(json.dumps(meta, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: meta[k] for k in
                      ("schema", "audit_complete", "units", "clock", "slack",
                       "period_min", "coverage")},
                     indent=2, sort_keys=True, allow_nan=False))
    return 0 if proc.returncode == 0 and parsed["audit_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
