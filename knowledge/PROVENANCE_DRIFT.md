# Provenance drift report (2026-11-23)

`verify-provenance` re-hashes every FDE source referenced by a knowledge record and compares it to
the hash captured at seed time. Result at this checkpoint:

```
status: DRIFT
checked: 42 source hashes
changed_count: 16
changed_sources: ["docs/decisions/DECISIONS.md"]
```

## Explanation (not a defect)

All 16 differences are the **same file**, `docs/decisions/DECISIONS.md`. At seed time the decision
index ended at D-023. Later in this same mission, decision **D-024** (the KB adoption decision) was
appended to that index. This is a legitimate append to a living document, not a change to any FDE
report or historical evidence.

Verified unchanged:
- All FDE reports `docs/FDE-003…FDE-007*.md`
- `MILESTONE_1C-R_DRT0305_ROOT_CAUSE_REPORT.md`
- agent reports, review/report logs, session handoffs
- baseline, design inputs, binaries, approval policy (see `verify-immutable`: 9/9 OK)

## Policy

The captured hashes are **point-in-time provenance**, deliberately preserved inside append-only
records. Drift is reported, never silently rewritten. A future curator that wants to record the new
state must append a new record with `record_version >= 2` and `relationships.supersedes` pointing at
the prior record — the original hash is never edited. This is why `verify-provenance` returns
`DRIFT` rather than modifying history.
