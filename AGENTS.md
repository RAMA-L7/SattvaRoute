# SattvaRoute — Agent Instructions

**Project:** SattvaRoute — AI-assisted physical-design orchestration and recovery.
**Root:** `D:\SattvaRoute` (WSL: `/mnt/d/SattvaRoute`) — **D drive only, never C.**
**EDA tools:** `D:\tools` (WSL: `/mnt/d/tools`) — never modify global installations.
**ORFS:** `D:\tools\OpenROAD-flow-scripts` (WSL: `/mnt/d/tools/OpenROAD-flow-scripts`), commit `25b6429`.

> AI never controls the PnR flow directly. Python controls stage execution; OpenROAD
> executes; parsers extract evidence; AI analyzes and proposes; an approval service
> authorizes; a deterministic controller applies approved patches and resumes.

## Mandatory reading order (before ANY work)

1. `AGENTS.md` (this file)
2. `PROJECT_STATE.md` — the single current snapshot
3. `coordination/ACTIVE_WORK.md` — who is doing what right now
4. `coordination/TASK_BOARD.md` — all tasks and their status
5. Recent entries in `logs/REVIEW_LOG.md`, `logs/REPORT_LOG.md`,
   `logs/DAILY_LOG.md`, `logs/AGENT_ACTIVITY.md`
6. Check `coordination/LOCKS/` — do not touch files another agent has locked

## Session lifecycle (mandatory)

**On start** — append a `SESSION START` block to `logs/DAILY_LOG.md` and a row to
`logs/AGENT_ACTIVITY.md` (timestamp ISO-8601 with timezone, agent, model, task,
starting git state, files expected to change).

**While working** — log engineering events only (discoveries, file changes, commands,
test results, blockers, decisions). Not every trivial command.

**On stop** — before ending: record completed/incomplete work, verification status,
files modified, known problems, commit status; then update `PROJECT_STATE.md`,
`logs/DAILY_LOG.md`, `logs/AGENT_ACTIVITY.md`, `coordination/TASK_BOARD.md`;
release locks; write an explicit `SESSION END` block with a handoff so another
agent can resume without repeating work. If interrupted unexpectedly, the next
agent reconstructs state from git, task board, logs and artifacts — never assumes
unfinished work succeeded.

## Agent roles

| Agent | Responsibility | File scope |
|---|---|---|
| Orchestrator | State, planning, task assignment, integration | coordination/*, PROJECT_STATE.md |
| EDA Agent | OpenFinRAM, macro integration, ORFS config, PnR | benchmark/, configs/, runs/, scripts/ |
| Architecture Agent | Backend, worker, persistence, workflow | app/, docs/architecture.md |
| Verification Agent | Tests, failure injection, correctness audits | tests/, audit reports |
| Documentation Agent | Reports, logs, reproducibility | logs/, docs/ |

Register a task in `coordination/TASK_BOARD.md` and take a lock in
`coordination/LOCKS/` before modifying files. Never let two agents modify the
same file. Verify your own changes before recording results.

## Project rules

1. D drive only for project files, dependencies, caches, outputs, artifacts. No extra C drive usage.
2. Never modify unrelated projects.
3. Never silently change RTL or the synthesized netlist.
4. Never overwrite previous runs. Each run/attempt is isolated.
5. Preserve logs and original artifacts.
6. Timestamps always include timezone.
7. Record every configuration change.
8. Require approval before applying recovery patches.
9. Verify claims with actual evidence. Exit code 0 ≠ success.
10. Clearly label simulation and mock results.
11. Maintain daily progress records; update project state before ending a session.
12. Check `logs/AGENT_ACTIVITY.md` before starting work.
13. Use subagents for independent tasks when supported; do not spawn agents for simple tasks.
14. No agent assumes another agent's task is complete without verification.

## Key environment facts (details: docs/milestone0-environment-audit.md)

- Windows 11-era build 26200 · i5-11300H 4C/8T · 15.79 GB RAM · WSL2 Ubuntu-24.04.4 (7.6 GiB, 2 GiB swap) · D: ~116 GB free
- OpenROAD `bazel-nostamp` headless at `/usr/local/bin/openroad` (8 threads) — no `-gui`
- Yosys: system 0.33 (`/usr/bin/yosys`, for ORFS) · yowasp-yosys 0.71 (`/root/.local/bin/yowasp-yosys`, WASM, for OpenFinRAM only — PATH shim in `scripts/gen_sram_macro.sh`)
- KLayout 0.30.13 (headless) + Python bindings 0.30.13 (user site)
- OpenFinRAM built at `benchmark/design/OpenFinRAM/build/OpenFinRAM` with the documented v2lvs patch (`src/openroad_manager.cpp`, fatal→warning)
- Verilator / Icarus are **Windows-only** (oss-cad-suite) — not available in WSL
- No Calibre, no tcsh → LVS path unavailable (non-fatal by design)
- WSL memory cap left at default 7.6 GiB (decision D-006)

## Milestone 1A — four required outputs

1. A macro-based controller benchmark that genuinely instantiates the OpenFinRAM SRAM.
2. A pinned, reproducible ORFS configuration.
3. A successful real baseline reaching the agreed physical-design endpoint — or a documented blocker with evidence.
4. A clean handoff in `PROJECT_STATE.md`.

Do **not** begin AI recovery implementation until the real baseline and its
limitations are documented.
