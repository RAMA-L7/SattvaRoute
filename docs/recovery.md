> **Historical / superseded for current documentation.** This note is preserved verbatim as engineering history. For the authoritative current recovery model, use `docs/architecture/RECOVERY.md`, `docs/architecture/APPROVAL.md`, and `docs/diagrams/RECOVERY_LIFECYCLE.md`. No technical meaning in this record was changed.

# Approval-gated recovery model

## Sequence

1. **Preserve** — never overwrite the failing run; record its ID and hashes.
2. **Observe** — collect stage logs, OpenDB state, tool source references, and version information.
3. **Hypothesize** — state a causal explanation that fits all evidence.
4. **Challenge** — have an independent analyst attempt to refute it from the same evidence.
5. **Decide** — write a decision record: root cause, exact modification, before/after diff, expected behavior, side effects, affected stages, rollback, verification plan.
6. **Approve** — obtain explicit human authorization before any edit or run.
7. **Apply one change** — to the tree the runner actually executes; record before/after hashes.
8. **Re-run** — new unique run ID.
9. **Verify** — report-level checks (D-007), including absence of the original error and presence of expected artifacts.
10. **Stop on a new failure** — preserve it; do not stack a second speculative fix.

## Case study: D-013 → D-014

- **D-013** (`set_special_nets [list zero_]`) was approved but failed: the command does not exist in this build; the edit targeted `D:\tools` while the runner sources the `D:\SattvaRoute\tools` mirror; and the insertion point was after the failing `pin_access`. It remains documented as a failed attempt.
- **D-014** replaced it with an OpenDB object-method call (`$net setSpecial`) in the executed mirror before `pin_access`, after four independent investigations and a read-only runtime probe. The experiment eliminated DRT-0305 but revealed a distinct DRT-0073 blocker; no further fix was applied.

## Rules

- No RTL, netlist, macro, SDC, placement, or layer changes to bypass an error.
- No suppressed errors, fabricated metrics, or relabeled failures.
- One variable at a time, with traceable approval and evidence.
