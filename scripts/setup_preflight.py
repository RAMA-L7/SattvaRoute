#!/usr/bin/env python3
"""Executable setup/preflight for the active supported profile.

Checks (read-only): pinned ORFS base + applicable patches, project/tool paths,
active-profile collateral, tool binaries and the GDS/KLayout dependency.
Actionable messages distinguish missing setup from engineering failures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", default="nangate_macro_control")
    p.add_argument("--mirror", default=os.environ.get("SATTVA_MIRROR", ""))
    p.add_argument("--allow-inactive", action="store_true",
                   help="do not require inactive historical profiles (default: skip them)")
    args = p.parse_args()
    problems: list[str] = []
    notes: list[str] = []

    cfg = json.loads((ROOT / "config" / "sattva_manifest.json").read_text(encoding="utf-8"))
    profile = cfg["profiles"].get(args.profile)
    if not profile:
        problems.append(f"unknown active profile {args.profile!r}")
        profile = {}
    mirror = Path(args.mirror or os.environ.get(
        "SATTVA_MIRROR", ROOT / "tools" / "OpenROAD-flow-scripts")).resolve()
    notes.append(f"SATTVA_ROOT={ROOT}")
    notes.append(f"SATTVA_MIRROR={mirror}")
    if not (mirror / ".git").exists():
        problems.append(f"ORFS mirror has no .git: {mirror}")

    patch_check = subprocess.run(
        ["python3", str(ROOT / "scripts" / "check_setup_patches.py"),
         "--mirror", str(mirror)], capture_output=True, text=True)
    print(patch_check.stdout.strip())
    if patch_check.returncode != 0:
        problems.append("ORFS setup patches are not applicable (see above)")

    for tool in ("openroad", "yosys"):
        expected = cfg["tools"][tool]["expected_sha256"]
        found = shutil.which(tool) or os.environ.get(
            "OPENROAD_EXE" if tool == "openroad" else "YOSYS_EXE")
        if not found:
            problems.append(f"{tool} not on PATH and no *_EXE override")
            continue
        actual = sha(Path(found))
        if actual != expected:
            problems.append(f"{tool} hash {actual} != pinned {expected}")
        else:
            notes.append(f"{tool} runtime identity OK ({found})")

    design_root = ROOT / str(profile.get("design_root", ""))
    for rel in profile.get("design_files", []):
        if not (design_root / rel).is_file():
            problems.append(f"active profile missing design file: {rel}")
    platform = mirror / str(profile.get("platform_dir", ""))
    for rel, want in (profile.get("platform_files") or {}).items():
        path = platform / rel
        if not path.is_file():
            problems.append(f"external platform collateral missing: {rel}")
        elif sha(path) != want:
            problems.append(f"external platform hash mismatch: {rel}")

    config = design_root / "config.mk"
    if config.is_file() and "/mnt/d/" in config.read_text(encoding="utf-8"):
        problems.append(f"author-specific path remains in {config}")
    kl = os.environ.get("KLAYOUT_CMD") or os.environ.get("SATTVA_KLAYOUT") or shutil.which("klayout")
    if kl:
        notes.append(f"KLayout/GDS dependency available: {kl}")
    else:
        problems.append("6_final.gds is a required endpoint artifact: set KLAYOUT_CMD/SATTVA_KLAYOUT "
                        "to a KLayout executable (GDS generation otherwise fails)")

    for note in notes:
        print("INFO " + note)
    if problems:
        for item in problems:
            print("FAIL " + item)
        return 1
    print(f"SETUP_PREFLIGHT_PASS profile={args.profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
