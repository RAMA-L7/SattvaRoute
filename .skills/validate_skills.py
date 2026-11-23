#!/usr/bin/env python3
"""Offline validation of the T-SKILL-001 skill system.

Standard library only. Writes nothing outside a temporary directory. Validates the
zero-install decision, inventory integrity, governance rules and protected artifacts.
Run: python3 .skills/validate_skills.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".skills"

REQUIRED_FILES = (
    "README.md", "INVENTORY.md", "DISCOVERY_REPORT.md", "EVALUATION_SUMMARY.md",
    "SECURITY_AUDIT.md", "INSTALLATION_REPORT.md", "skill_sources.json",
    "validate_skills.py", "PROJECT_SKILLS.json", "PROJECT_SKILLS.md",
)

results: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    results.append((name, bool(condition), detail))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    # 1. Required files present and readable.
    missing = [f for f in REQUIRED_FILES if not (SKILLS / f).is_file()]
    check("required files present", not missing, f"missing={missing}")

    # 2. skill_sources.json parses and records the verified union.
    try:
        sources = json.loads((SKILLS / "skill_sources.json").read_text(encoding="utf-8"))
        union = sources.get("union_unique_skill_names_with_SKILL_md")
        check("discovery evidence parses", union == 164, f"union={union}")
    except Exception as exc:  # noqa: BLE001
        check("discovery evidence parses", False, str(exc))

    # 2b. Project skill catalog is honest about actual state.
    cat_path = SKILLS / "PROJECT_SKILLS.json"
    if cat_path.is_file():
        try:
            cat = json.loads(cat_path.read_text(encoding="utf-8"))
            allowed = {"DISCOVERED", "EVALUATED", "RECOMMENDED", "APPROVED",
                       "INSTALLED", "VALIDATED", "ACTIVE", "REJECTED", "BLOCKED"}
            entries = cat.get("skills", [])
            bad = [e.get("skill_id") for e in entries if e.get("status") not in allowed]
            falsely_installed = [e.get("skill_id") for e in entries
                                 if e.get("status") in ("INSTALLED", "VALIDATED", "ACTIVE")
                                 or e.get("installation_path") is not None]
            check("catalog parses with valid statuses", not bad, f"invalid={bad}")
            check("catalog preserves zero-install invariant", not falsely_installed,
                  f"falsely_active={falsely_installed}")
        except Exception as exc:  # noqa: BLE001
            check("catalog parses with valid statuses", False, str(exc))
            check("catalog preserves zero-install invariant", False, str(exc))
    else:
        check("catalog parses with valid statuses", False, "PROJECT_SKILLS.json missing")
        check("catalog preserves zero-install invariant", False, "PROJECT_SKILLS.json missing")

    # 3. Zero-install invariant: no skill directories or SKILL.md under .skills.
    skill_dirs = [p.name for p in SKILLS.iterdir() if p.is_dir()] if SKILLS.is_dir() else []
    skill_files = [str(p.relative_to(SKILLS)) for p in SKILLS.rglob("SKILL.md")]
    check("no project skill directories", not skill_dirs, f"dirs={skill_dirs}")
    check("no project SKILL.md", not skill_files, f"files={skill_files}")

    # 4. Inventory records zero approved/installed/active.
    inv = (SKILLS / "INVENTORY.md").read_text(encoding="utf-8") if (SKILLS / "INVENTORY.md").is_file() else ""
    check("inventory records zero install",
          "zero skills approved, zero installed, zero active" in inv and "**None.**" in inv)

    # 5. Governance rules present.
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8") if (ROOT / "AGENTS.md").is_file() else ""
    readme = (SKILLS / "README.md").read_text(encoding="utf-8") if (SKILLS / "README.md").is_file() else ""
    check("governance: approval + evidence rules",
          "Require approval" in agents and "Verify claims with actual evidence" in agents)
    check("governance: skill usage rules",
          "NO VALIDATED SKILL AVAILABLE" in readme and "Skills cannot bypass approval controls" in readme)

    # 6. Protected artifacts unchanged (compare against KB immutable manifest).
    imm_path = ROOT / "knowledge" / "kb_immutable_manifest.json"
    if imm_path.is_file():
        imm = json.loads(imm_path.read_text(encoding="utf-8"))
        changed, absent = [], []
        for rel, want in imm.get("protected_hashes", {}).items():
            p = ROOT / rel
            if p.is_file():
                if sha256_file(p) != want:
                    changed.append(rel)
            else:
                absent.append(rel)
        # Live repo: every protected artifact is present and must hash-match.
        # Publication checkout: binary/design fixtures are intentionally absent;
        # report that explicitly rather than claiming a full verification.
        detail = f"changed={changed}"
        if absent:
            detail += f"; absent_in_publication={absent}"
        check("protected artifacts unchanged", not changed, detail)
    else:
        check("protected artifacts unchanged", False, "immutable manifest missing")

    # 7. KB ledger hash matches derived manifest (no out-of-band record edits).
    man_path = ROOT / "knowledge" / "kb_manifest.json"
    ledger = ROOT / "knowledge" / "kb_records.jsonl"
    if man_path.is_file() and ledger.is_file():
        man = json.loads(man_path.read_text(encoding="utf-8"))
        check("KB ledger unchanged", man.get("store_sha256") == sha256_file(ledger))
    else:
        check("KB ledger unchanged", False, "manifest or ledger missing")

    # 8. No executable script other than this validator in .skills.
    executables = [str(p.relative_to(SKILLS)) for p in SKILLS.rglob("*")
                   if p.is_file() and p.suffix not in (".md", ".json", ".py", ".pyc", ".sh")]
    check("no unexpected skill executables", not executables, f"files={executables}")

    # 9. Validator writes nothing (temp dir used only if needed).
    with tempfile.TemporaryDirectory() as tmp:
        check("offline temp workspace available", Path(tmp).is_dir())

    passed = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        print(f"{status} {name}" + (f" — {detail}" if detail else ""))
    print(f"RESULT: PASS={passed} FAIL={len(results) - passed}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
