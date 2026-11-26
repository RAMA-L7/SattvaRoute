# Decision records

Status: points to authoritative existing records. Existing decision history is preserved and not rewritten.

## Authoritative decision index

`docs/decisions/DECISIONS.md` is the authoritative engineering decision index (D-xxx records). `docs/REPORT_INDEX.md` indexes historical engineering reports. Neither was modified in this documentation milestone.

## Selected record references

| Decision / milestone | Record | Note |
|---|---|---|
| D-014 | `docs/decisions/D-014_proposal.md`, manifest local patch | Mark `zero_` net SPECIAL before first TritonRoute call (DRT-0305); patch hash pinned |
| D-021 | `docs/decisions/DECISIONS.md` | Root cause record; no remedy approved |
| D-022 / D-023 | `docs/decisions/DECISIONS.md` | R1-N / R1-N-W approved then rejected |
| D-025 / D-026 / D-027 | `docs/decisions/DECISIONS.md` | Skills-related decisions |
| 1 ns SDC correction | `docs/TIMING_AUDIT.md`, `constraint_1ns.sdc`, approval records | Explicitly approved; original `constraint.sdc` preserved |
| Held-out LEF recovery | `docs/HELDOUT_RECOVERY.md`, `AP-HELDOUT-LEFS-001` | Deterministic diagnosis; human-approved; verified PASS |
| Publication | `PROJECT_STATE.md`, PR #1 | `PUBLISHED_REMOTE`, `PR_MERGED_VERIFIED` |

## Decision-record convention for future work

A decision record should state: context/evidence, options considered, decision, exact diff or action, rollback path, verification plan, approval status, and date (UTC). Do not rewrite a historical decision to match a newer narrative; append a superseding record and link it.

## Related

`docs/governance/GOVERNANCE.md`, `docs/REPORT_INDEX.md`, `docs/audit/SCOPE_INTEGRITY.md`.
