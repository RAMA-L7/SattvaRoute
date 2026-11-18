# LOCKS

One lock file per active task: `<task-id>.lock`

Contents (plain text):

```text
task: T-M1-001
agent: orchestrator (EDA role)
model: mimo-v2.6-flash-free
acquired: 2026-11-18T18:50:42+05:30
files:
  benchmark/design/sattva_sram/**
  docs/benchmark/**
```

Rules:
- Acquire before modifying files; release when work is verified and logged.
- Never modify files listed in another task's lock.
- If a lock is stale (no matching IN_PROGRESS row in ACTIVE_WORK.md), treat it as
  suspect: reconstruct state from git and logs before touching the files.
