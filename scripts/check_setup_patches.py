#!/usr/bin/env python3
"""Check that published ORFS setup patches are applicable and produce pinned files.

Read-only: verifies the pinned base revision, patch hashes, applicability to the
clean git index, and the SHA-256 of each patched file computed in memory from
the base blob. It never applies a patch to a working tree or changes a mirror.

Usage:
  python3 scripts/check_setup_patches.py [--mirror <orfs-checkout>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PATCH_DIR = ROOT / "patches" / "orfs"
PATCH_MANIFEST = PATCH_DIR / "manifest.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply_unified_diff(text: str, diff: str) -> str:
    """Apply a simple unified diff in memory; rejects context mismatches."""
    src = text.splitlines(keepends=True)
    out: list[str] = []
    pos = 0
    lines = diff.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("@@"):
            i += 1
            continue
        header = line
        import re
        m = re.search(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", header)
        if not m:
            raise ValueError("malformed hunk header")
        start = int(m.group(1)) - 1
        if start < pos or start > len(src):
            raise ValueError("hunk out of order")
        out.extend(src[pos:start])
        pos = start
        i += 1
        while i < len(lines) and not lines[i].startswith("@@") and not lines[i].startswith("diff "):
            h = lines[i]
            if h.startswith(" "):
                expected = h[1:]
                if pos >= len(src) or src[pos].rstrip("\n") != expected.rstrip("\n"):
                    raise ValueError(f"context mismatch at line {pos + 1}")
                out.append(src[pos]); pos += 1
            elif h.startswith("-"):
                expected = h[1:]
                if pos >= len(src) or src[pos].rstrip("\n") != expected.rstrip("\n"):
                    raise ValueError(f"removal mismatch at line {pos + 1}")
                pos += 1
            elif h.startswith("+"):
                out.append(h[1:] + "\n")
            elif h.startswith("\\"):
                pass
            else:
                raise ValueError(f"unexpected diff line: {h!r}")
            i += 1
    out.extend(src[pos:])
    return "".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mirror", default=os.environ.get(
        "SATTVA_MIRROR", str(ROOT / "tools" / "OpenROAD-flow-scripts")))
    args = p.parse_args()
    mirror = Path(args.mirror).resolve()
    cfg = json.loads(PATCH_MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []

    if not (mirror / ".git").exists():
        failures.append(f"no git checkout at {mirror}")
        head = None
    else:
        head = subprocess.run(["git", "-C", str(mirror), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        if head != cfg["base_revision"]:
            failures.append(f"HEAD {head} != pinned base {cfg['base_revision']}")

    for row in cfg["patches"]:
        path = PATCH_DIR / row["file"]
        if not path.is_file():
            failures.append(f"missing patch {row['file']}")
            continue
        patch = path.read_text(encoding="utf-8")
        if sha256(patch.encode()) != row["sha256"]:
            failures.append(f"patch hash mismatch: {row['file']}")
        if head == cfg["base_revision"]:
            check = subprocess.run(["git", "-C", str(mirror), "apply",
                                    "--check", "--cached", str(path)],
                                   capture_output=True, text=True)
            if check.returncode != 0:
                failures.append(f"patch not applicable to clean index: {row['file']}: "
                                + check.stderr.strip())
            blob = subprocess.run(["git", "-C", str(mirror), "show",
                                   f"HEAD:{row['target']}"],
                                  capture_output=True, text=True)
            if blob.returncode != 0:
                failures.append(f"cannot read base blob for {row['target']}")
                continue
            try:
                result = apply_unified_diff(blob.stdout, patch)
                actual = sha256(result.encode())
                if actual != row["expected_result_sha256"]:
                    failures.append(f"result hash mismatch for {row['target']}: {actual}")
                print(f"OK {row['file']} -> {row['target']} {actual[:16]}")
            except ValueError as exc:
                failures.append(f"in-memory apply failed for {row['file']}: {exc}")

    if failures:
        for item in failures:
            print("FAIL " + item)
        return 1
    print(f"SETUP_PATCHES_PASS base={cfg['base_revision']} patches={len(cfg['patches'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
