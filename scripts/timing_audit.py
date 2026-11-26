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
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TCL = ROOT / "scripts" / "audit_timing.tcl"

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


def parse(raw: str) -> dict[str, Any]:
    units = {k: v for k, v in UNIT_RE.findall(section(raw, "REPORT_UNITS"))}
    clock = None
    cm = CLOCK_RE.search(section(raw, "CLOCK_PROPERTIES"))
    if cm:
        clock = {"name": cm.group(1), "period": float(cm.group(2)),
                 "waveform": [float(cm.group(3)), float(cm.group(4))]}
    slack = {m.group(1): float(m.group(2))
             for m in WORST_RE.finditer(section(raw, "WORST_SLACK"))}

    def min_period(name: str) -> dict[str, Any]:
        m = PERIOD_RE.search(section(raw, name))
        if not m:
            return {"period_min": None, "fmax": None}
        return {"period_min": (None if m.group(1) == "inf" else float(m.group(1))),
                "fmax": (None if m.group(2) == "inf" else m.group(2))}

    coverage = {}
    for key in ("input_ports", "output_ports", "register_clock_pins",
                "registers", "clocks"):
        m = re.search(rf"^{key} (\d+)$", section(raw, "COVERAGE"), re.M)
        coverage[key] = int(m.group(1)) if m else None

    check_setup = section(raw, "CHECK_SETUP").strip()
    warnings = [ln for ln in check_setup.splitlines()
                if ln.strip() and not ln.startswith("SECTION_ERROR")]
    coverage["unconstrained_endpoints"] = len(warnings)
    coverage["check_setup_text"] = check_setup

    par = section(raw, "PARASITICS")
    coverage["parasitics"] = {
        "unannotated_drivers": (int(UNANNOTATED_RE.search(par).group(1))
                                if UNANNOTATED_RE.search(par) else None),
        "partially_unannotated_drivers": (int(m.group(1))
                                          if (m := re.search(
                                              r"Found\s+(\d+)\s+partially unannotated drivers", par))
                                          else None),
    }
    return {
        "units": units,
        "clock": clock,
        "slack": slack,
        "period_min": {
            "reg_to_reg": min_period("MIN_PERIOD_REG_TO_REG"),
            "including_ports": min_period("MIN_PERIOD_INCLUDING_PORTS"),
        },
        "coverage": coverage,
        "parasitics": coverage.pop("parasitics"),
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

    meta = {
        "run": str(run),
        "results_dir": str(results),
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
    meta.update(parse(raw))
    out.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: meta[k] for k in
                      ("units", "clock", "slack", "period_min", "coverage")},
                     indent=2, sort_keys=True))
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
