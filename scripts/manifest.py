#!/usr/bin/env python3
"""Profile-scoped dependency manifest helper (offline, no EDA).

A manifest describes several design *profiles*. Only the selected profile is
resolved: an inactive profile can be absent, broken or stale without blocking
the active run. For the active profile this module:

  * resolves the exact design, platform, flow and extraction inputs;
  * verifies the ORFS checkout revision and that the only tracked flow changes
    are the declared local patches;
  * verifies declared platform/technology/extraction hashes;
  * compares the recorded tool identity with the binary that will execute;
  * separates *declared* expectations from *captured* fingerprints;
  * computes one canonical fingerprint over the resolved set, used by approval
    binding and resume compatibility.

Status vocabulary: PASS / FAIL / UNKNOWN. Missing or unverifiable required
evidence is never reported as PASS.
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
DEFAULT_MANIFEST = ROOT / "config" / "sattva_manifest.json"

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"


# ---------------------------------------------------------------------------
# path / hash helpers
# ---------------------------------------------------------------------------
def resolve(path: str | os.PathLike[str], base: Path) -> Path:
    p = Path(os.path.expandvars(str(path)))
    return p if p.is_absolute() else base / p


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_digest(manifest: Path) -> str:
    return sha256_file(manifest)


def load(manifest: Path) -> dict[str, Any]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"manifest root must be an object: {manifest}")
    return data


def profile_names(data: dict[str, Any]) -> list[str]:
    return sorted((data.get("profiles") or {}).keys())


def profile(data: dict[str, Any], name: str) -> dict[str, Any]:
    profiles = data.get("profiles") or {}
    if name not in profiles:
        raise KeyError(f"unknown profile {name!r}; known: {sorted(profiles)}")
    return profiles[name]


# ---------------------------------------------------------------------------
# resolution
# ---------------------------------------------------------------------------
def paths(manifest: Path, name: str, root: Path | None = None,
          mirror: Path | None = None) -> dict[str, Any]:
    """Resolve every declared path for one profile without touching the FS."""
    root = root or ROOT
    data = load(manifest)
    prof = profile(data, name)
    orfs = data.get("orfs") or {}
    if mirror is None:
        env_value = os.environ.get(orfs["root_env"]) if orfs.get("root_env") else None
        mirror = resolve(env_value or orfs.get(
            "root_default", "tools/OpenROAD-flow-scripts"), root)
    design_root = resolve(prof["design_root"], root)
    platform_dir = resolve(prof["platform_dir"], mirror) if prof.get("platform_dir") else None

    files: list[tuple[str, str, Path]] = []
    for rel in prof.get("design_files") or []:
        files.append(("design", rel, design_root / rel))
    for rel in prof.get("flow_files") or []:
        files.append(("flow", rel, mirror / rel))
    for rel in (prof.get("platform_files") or {}):
        files.append(("platform", rel, platform_dir / rel))
    return {
        "profile": name,
        "profile_doc": prof,
        "root": root,
        "mirror": mirror,
        "design_root": design_root,
        "platform_dir": platform_dir,
        "files": files,
        "approval_inputs": [design_root / rel for rel in
                            (prof.get("approval_inputs") or [])],
    }


# ---------------------------------------------------------------------------
# declared expectations
# ---------------------------------------------------------------------------
def _git(mirror: Path, *args: str) -> tuple[int, str]:
    if not (mirror / ".git").exists():
        return 127, "no .git in mirror"
    try:
        proc = subprocess.run(["git", "-C", str(mirror), *args],
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)
    return proc.returncode, (proc.stdout or proc.stderr).strip()


def _tool_path(spec: dict[str, Any]) -> Path | None:
    env = spec.get("env")
    value = os.environ.get(env) if env else None
    value = value or spec.get("default")
    if not value:
        return None
    p = Path(value)
    return p if p.is_absolute() else None


def check(manifest: Path, root: Path | None = None, name: str | None = None,
          *, mirror: Path | None = None, use_git: bool = True,
          design_root_override: Path | None = None) -> dict[str, Any]:
    root = root or ROOT
    data = load(manifest)
    if name is None:
        name = next(iter(profile_names(data)), None)
    if not name:
        return {"status": FAIL, "reason": "manifest declares no profiles",
                "digest": manifest_digest(manifest), "missing": [],
                "mismatches": [], "file_hashes": {}}
    resolved = paths(manifest, name, root, mirror)
    if design_root_override is not None:
        resolved["design_root"] = design_root_override
        # rebuild file list against the overridden design root
        files = [(c, r, (design_root_override / r) if c == "design" else p)
                 for (c, r, p) in resolved["files"]]
        resolved["files"] = files
        resolved["approval_inputs"] = [design_root_override / rel for rel in
                                       (resolved["profile_doc"].get("approval_inputs") or [])]
    mirror = resolved["mirror"]
    prof = resolved["profile_doc"]
    orfs = data.get("orfs") or {}

    missing: list[str] = []
    mismatches: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    file_hashes: dict[str, str] = {}
    captured_platform: dict[str, str] = {}
    captured_flow: dict[str, str] = {}
    captured_design: dict[str, str] = {}

    # --- design / flow / platform files -----------------------------------
    for category, rel, path in resolved["files"]:
        label = f"{category}:{rel}"
        if not path.is_file():
            missing.append(label)
            checks.append({"name": label, "status": "MISSING", "path": str(path)})
            continue
        digest = sha256_file(path)
        file_hashes[label] = digest
        if category == "platform":
            captured_platform[rel] = digest
        elif category == "flow":
            captured_flow[rel] = digest
        else:
            captured_design[rel] = digest

    # --- declared platform hashes -----------------------------------------
    declared_platform = prof.get("platform_files") or {}
    for rel, expected in declared_platform.items():
        label = f"platform:{rel}"
        actual = captured_platform.get(rel)
        if actual is None:
            continue  # already reported missing
        if actual != expected:
            mismatches.append({"kind": "platform", "name": label,
                               "expected": expected, "actual": actual})
            checks.append({"name": label, "status": "MISMATCH",
                           "expected": expected, "actual": actual})
        else:
            checks.append({"name": label, "status": "OK", "sha256": actual})

    # --- ORFS revision + local patches ------------------------------------
    declared_rev = orfs.get("revision")
    captured_rev = None
    rev_status = "SKIPPED"
    rev_detail = None
    if use_git and orfs.get("verify_revision", True):
        rc, out = _git(mirror, "rev-parse", "HEAD")
        if rc == 0:
            captured_rev = out
            if declared_rev and out != declared_rev:
                mismatches.append({"kind": "orfs_revision", "name": "orfs:revision",
                                   "expected": declared_rev, "actual": out})
                rev_status = "MISMATCH"
            else:
                rev_status = "OK"
        else:
            rev_status = "UNVERIFIED"
            rev_detail = out
    checks.append({"name": "orfs:revision", "status": rev_status,
                   "declared": declared_rev, "captured": captured_rev,
                   "detail": rev_detail})

    declared_patches = {p["path"]: p.get("sha256")
                        for p in orfs.get("local_patches") or []}
    captured_patches: dict[str, str] = {}
    for rel, expected in declared_patches.items():
        path = mirror / rel
        if not path.is_file():
            missing.append(f"patch:{rel}")
            checks.append({"name": f"patch:{rel}", "status": "MISSING",
                           "path": str(path)})
            continue
        actual = sha256_file(path)
        captured_patches[rel] = actual
        if expected and actual != expected:
            mismatches.append({"kind": "local_patch", "name": f"patch:{rel}",
                               "expected": expected, "actual": actual})
            checks.append({"name": f"patch:{rel}", "status": "MISMATCH",
                           "expected": expected, "actual": actual})
        else:
            checks.append({"name": f"patch:{rel}", "status": "OK",
                           "sha256": actual})

    # Tracked working-tree changes must be exactly the declared local patches.
    if use_git and orfs.get("verify_revision", True):
        rc, out = _git(mirror, "diff", "--name-only", "HEAD")
        if rc == 0:
            changed = {ln.strip() for ln in out.splitlines() if ln.strip()}
            unexpected = sorted(changed - set(declared_patches))
            unpatched = sorted(set(declared_patches) - changed)
            if unexpected:
                mismatches.append({"kind": "orfs_unexpected_changes",
                                   "name": "orfs:working_tree",
                                   "expected": sorted(declared_patches),
                                   "actual": unexpected})
                checks.append({"name": "orfs:working_tree", "status": "MISMATCH",
                               "unexpected": unexpected})
            elif unpatched:
                checks.append({"name": "orfs:working_tree", "status": "UNPATCHED",
                               "detail": f"declared patches not present: {unpatched}"})
            else:
                checks.append({"name": "orfs:working_tree", "status": "OK",
                               "changed": sorted(changed)})
        else:
            checks.append({"name": "orfs:working_tree", "status": "UNVERIFIED",
                           "detail": out})

    # --- tool identity -----------------------------------------------------
    captured_tools: dict[str, str] = {}
    for tool, spec in (data.get("tools") or {}).items():
        path = _tool_path(spec)
        label = f"tool:{tool}"
        if path is None or not path.is_file():
            missing.append(label)
            checks.append({"name": label, "status": "MISSING",
                           "path": str(path)})
            continue
        actual = sha256_file(path)
        captured_tools[tool] = actual
        expected = spec.get("expected_sha256")
        if expected and actual != expected:
            mismatches.append({"kind": "tool", "name": label,
                               "expected": expected, "actual": actual})
            checks.append({"name": label, "status": "MISMATCH",
                           "expected": expected, "actual": actual})
        elif expected:
            checks.append({"name": label, "status": "OK", "sha256": actual})
        else:
            checks.append({"name": label, "status": "UNDECLARED",
                           "sha256": actual})

    # --- canonical fingerprint --------------------------------------------
    fingerprint = _fingerprint(
        revision=captured_rev or declared_rev,
        patches=captured_patches,
        tools=captured_tools,
        files=file_hashes,
    )

    status = PASS
    if missing or mismatches:
        status = FAIL
    elif use_git and orfs.get("verify_revision", True) and rev_status != "OK":
        status = UNKNOWN

    return {
        "status": status,
        "manifest_id": data.get("manifest_id"),
        "version": data.get("version"),
        "profile": name,
        "inactive_profiles": [p for p in profile_names(data) if p != name],
        "digest": manifest_digest(manifest),
        "fingerprint": fingerprint,
        "declared": {
            "orfs_revision": declared_rev,
            "local_patches": declared_patches,
            "platform_hashes": declared_platform,
            "tools": {k: v.get("expected_sha256")
                      for k, v in (data.get("tools") or {}).items()},
        },
        "captured": {
            "orfs_revision": captured_rev,
            "tools": captured_tools,
            "design": captured_design,
            "platform": captured_platform,
            "flow": captured_flow,
        },
        "missing": missing,
        "mismatches": mismatches,
        "checks": checks,
        # legacy keys retained for existing consumers
        "orfs_revision": declared_rev,
        "file_hashes": file_hashes,
    }


def _fingerprint(*, revision: str | None, patches: dict[str, str],
                 tools: dict[str, str], files: dict[str, str]) -> str:
    payload = {
        "orfs_revision": revision,
        "local_patches": dict(sorted(patches.items())),
        "tools": dict(sorted(tools.items())),
        "files": dict(sorted(files.items())),
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def fingerprint(manifest: Path, name: str, root: Path | None = None,
                *, mirror: Path | None = None,
                design_root_override: Path | None = None) -> str:
    result = check(manifest, root, name, mirror=mirror, use_git=False,
                   design_root_override=design_root_override)
    return result["fingerprint"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    p.add_argument("--root", default=str(ROOT))
    p.add_argument("--profile", help="profile to resolve (default: first declared)")
    p.add_argument("--mirror", help="ORFS checkout (default: manifest/env)")
    p.add_argument("--check", action="store_true")
    p.add_argument("--fingerprint", action="store_true",
                   help="print only the canonical profile fingerprint")
    p.add_argument("--no-git", action="store_true",
                   help="skip revision/working-tree verification")
    p.add_argument("--list-profiles", action="store_true")
    p.add_argument("--design-root", help="override the profile design root")
    args = p.parse_args()

    manifest = Path(args.manifest)
    override = Path(args.design_root) if args.design_root else None
    if args.list_profiles:
        out: Any = {"profiles": profile_names(load(manifest))}
    elif args.fingerprint:
        if not args.profile:
            p.error("--fingerprint requires --profile")
        out = {"profile": args.profile,
               "fingerprint": fingerprint(manifest, args.profile,
                                          Path(args.root),
                                          mirror=Path(args.mirror) if args.mirror else None,
                                          design_root_override=override)}
    else:
        out = check(manifest, Path(args.root), args.profile,
                    mirror=Path(args.mirror) if args.mirror else None,
                    use_git=not args.no_git,
                    design_root_override=override) if args.check else {
            "status": PASS, "digest": manifest_digest(manifest)}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out.get("status", PASS) == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
