#!/usr/bin/env python3
"""Shared dependency manifest helper (offline, no EDA).

Computes a canonical SHA-256 digest of the manifest and verifies that every
declared existing path is present. Used by runner preflight, approval binding,
resume compatibility checks and the final evidence bundle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "config" / "sattva_manifest.json"


def resolve(path: str, root: Path) -> Path:
    p = Path(os.path.expandvars(path))
    return p if p.is_absolute() else root / p


def manifest_digest(manifest: Path) -> str:
    return hashlib.sha256(manifest.read_bytes()).hexdigest()


def expand(manifest: Path, root: Path | None = None) -> dict[str, Any]:
    root = root or ROOT
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["_root"] = str(root)
    data["_digest"] = manifest_digest(manifest)
    return data


def check(manifest: Path, root: Path | None = None) -> dict[str, Any]:
    data = expand(manifest, root)
    root = Path(data["_root"])
    missing: list[str] = []
    files: dict[str, str] = {}
    for rel in data.get("flow_files", []):
        p = resolve(rel, root)
        if not p.is_file():
            missing.append(rel)
        else:
            files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    for name in ("policy", "approval_tool", "runner"):
        rel = data.get(name)
        if rel:
            p = resolve(rel, root)
            if not p.is_file():
                missing.append(rel)
            else:
                files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    for d in data.get("designs", {}).values():
        base = resolve(d["path"], root)
        for key in ("config", "sdc", "pdn", "macro_placement", "netlist",
                    "provenance", "rtl_top", "rtl_blackbox", "macro_lef",
                    "macro_lib", "macro_gds"):
            rel = d.get(key)
            if not rel:
                continue
            p = base / rel
            if not p.is_file():
                missing.append(str(p.relative_to(root)))
            else:
                files[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    orfs_rev = data.get("orfs", {}).get("revision")
    return {"status": "PASS" if not missing and orfs_rev else "FAIL",
            "digest": data["_digest"], "missing": missing,
            "file_hashes": files, "orfs_revision": orfs_rev}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    p.add_argument("--root", default=str(ROOT))
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    out = check(Path(args.manifest), Path(args.root)) if args.check else {
        "status": "PASS", "digest": manifest_digest(Path(args.manifest))}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
