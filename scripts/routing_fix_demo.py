#!/usr/bin/env python3
"""RETIRED demonstration (2026-11-19) — do not execute as a recovery action.

Why retired:
  * The original file was a shell script pasted into a .py file and failed
    compilation (`SyntaxError` at line 17).
  * It advertised "D-013 — special-net assignment applied" while doing only
    `mkdir`, `cp` and an echo; D-013 was later proven FAILED (the command
    `set_special_nets` does not exist in this OpenROAD build, the edit targeted
    the unused D:\tools checkout, and it was placed after the failing call).
  * It referenced a run ID (`orfs_baseline_20261119T103000Z`) that does not
    exist in `runs/`.

Replacement references:
  * D-013 failure record: docs/decisions/DECISIONS.md
  * D-014 applied fix and evidence: docs/decisions/D-014_proposal.md §10
  * Real exact-patch approval + application: scripts/sattva_approval.py
  * Tested boundary integration: scripts/run_baseline_orfs.sh, tests/test_approval.py

This file is kept only to document the retired attempt. It never edits design
files, flow scripts or run artifacts.
"""
print("RETIRED: routing_fix_demo.py was a non-executable D-013 demonstration.")
print("D-013 FAILED; see docs/decisions/DECISIONS.md and D-014_proposal.md section 10.")
print("Use scripts/sattva_approval.py for validated, exact-patch recovery.")
