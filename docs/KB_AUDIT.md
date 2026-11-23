# SattvaRoute KB Mission — Phase 0 Audit, Capability Inventory and Integration Plan

- **Date:** 2026-11-23
- **Task:** T-KB-001
- **Method:** direct inspection of repository structure, source, tests, docs, logs and git state.
  Documentation claims were checked against code and tests where possible.
- **Read-only on:** `benchmark/`, `runs/`, `experiments/`, `tools/`, `configs/`,
  `state/approval_policy.json`. No design, baseline, binary or flow input changed.

## 1. Starting state (verified)

| Item | Observation |
|---|---|
| Publication repo | `D:\SattvaRoute_publish`, branch `main`, HEAD `35fe33c7f63a18b26a94af33c34171d21ad8c663`, equals `origin/main`, clean tree |
| Live repo | `D:\SattvaRoute`, branch `master`, HEAD `3d7b936`; extensive uncommitted FDE records, experiments, runs, scripts and docs |
| Source baseline | `runs/orfs_baseline_20261119T131025284719666Z_9263`; `4_cts.odb` SHA-256 `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` |
| Installed binary | `/usr/local/bin/openroad` SHA-256 `c1b90e0af69bc9779cde8fd1579a92a10738ddebb9ea16e459f280556c349ee9` |
| Production macro views | LEF `f1c18877…`, GDS `12c56777…`, Liberty estimated; unchanged |
| Locks | Only `coordination/LOCKS/README.md`; no active task lock at start |

The live/publication split is intentional: the live tree holds working FDE evidence and the publish
tree holds authoritative committed history. Both were preserved; no uncommitted work was discarded.

## 2. Repository structure and where a KB attaches

| Directory | Actual contents | KB relevance |
|---|---|---|
| `docs/` | FDE-003..FDE-007 reports, DRT-0305 report, decisions index, benchmark doc | Historical evidence; seed source; FDE remains authoritative |
| `reports/` | Four agent reports (A–D) on DRT-0305 | Seed evidence |
| `scripts/` | `run_baseline_orfs.sh`, `sattva_approval.py`, macro/ABC/test helpers | Reuse patterns: ledger, strict validation, atomic writes, locks |
| `state/` | `approval_policy.json` (and ledger if created) | Safety boundary; must not change |
| `tests/` | `test_approval.py`, `test_runner.sh` | Regression baseline; test style to follow |
| `coordination/` | task board, active work, locks | Orchestration state; update only |
| `logs/` | daily, agent activity, review, report logs; session handoffs | Chronological history; append only |
| `runs/`, `experiments/` | immutable baselines and isolated scratch runs | Read-only evidence; never rewritten |
| `benchmark/`, `configs/`, `tools/` | design inputs, ORFS config and LF execution mirror | Protected; read-only for this mission |
| `app/` | empty | No backend to extend; do not invent one |

Conclusion: there is no application backend or existing KB store to extend. The smallest safe
integration is a standalone stdlib module under `scripts/` writing a JSONL ledger under a new
`knowledge/` directory, following the approval module's proven pattern.

## 3. Existing capability inventory

Legend: **PRESENT** = implemented and tested; **PARTIAL** = exists in an informal form;
**MISSING** = no implementation found.

| Capability | Status | Evidence |
|---|---|---|
| Repository architecture / execution pipeline | PRESENT | `AGENTS.md`, `scripts/run_baseline_orfs.sh`, stage-based ORFS flow |
| Investigation workflow / FDE system | PRESENT | `docs/FDE-003…FDE-007*.md`, `logs/REPORT_LOG.md`, decision IDs D-001..D-023 |
| Experiment history | PRESENT | `experiments/`, `runs/`, `logs/AGENT_ACTIVITY.md`, session handoffs |
| Baseline management | PRESENT | collision-safe run IDs, `run.json`, `preflight.json`, `artifact_sha256.txt`, immutable runs; FDE-001 14/14 tests |
| Scratch environment / isolation | PRESENT | scratch LEFs under `experiments/FDE-007/*/scratch_design`; production LEF unchanged |
| Agent orchestration | PRESENT | `coordination/TASK_BOARD.md`, `ACTIVE_WORK.md`, `LOCKS/`, multi-agent FDE-007 A–D |
| Evidence collection | PRESENT | per-stage logs, hashes, manifests, `stages.txt`, reviewer findings |
| Validation framework | PARTIAL | stage rc + artifact checks and D-007 policy exist; no report-level *automatic* PASS adjudicator |
| Safety controls / approval gates | PRESENT | `sattva_approval.py` 25/25 tests, `state/approval_policy.json`, D-007, review gates |
| Storage and schemas | PARTIAL | JSON approval records + JSONL ledger pattern exists; no knowledge schema |
| Tests | PRESENT | `test_approval.py` (25/25), `test_runner.sh` (14/14) |
| Documentation | PRESENT | extensive but prose-only; no structured, queryable knowledge |
| **Structured Knowledge Base** | **MISSING** | no typed records, schema, provenance hashes, retrieval, ranking, applicability, maturity or duplicate suppression |
| **Cross-design reuse model** | **MISSING** | no design fingerprint or compatibility assessment mechanism |
| **FDE → KB capture** | **MISSING** | FDEs produce prose reports only; no machine-readable capture step |

## 4. Gap analysis for the KB mission

1. **Record structure** — no machine-readable record carrying identity/provenance, failure
   characteristics, hypothesis/root cause, remedy family, experiment, outcome state, applicability,
   separated evidence and maturity.
2. **Append-oriented versioning** — approval ledger is append-only; knowledge needs the same
   discipline plus per-record integrity hashes and `supersedes` links for corrections.
3. **Retrieval and explanation** — no search over historical cases; retrieval must be transparent
   (decomposed factors) and must never fabricate results.
4. **Applicability engine** — no gating between retrieval and remedy recommendation; needed classes
   STRONG/PARTIAL/INCOMPATIBLE/PREVIOUSLY_FAILED/NO_RELEVANT_KNOWLEDGE/INSUFFICIENT_EVIDENCE.
5. **Design-specific vs reusable** — prose describes SRAM geometry and general principles together;
   no field-level classification or cross-design compatibility check.
6. **Failed experiment learning** — failed attempts are documented but not deduplicated by remedy
   family. Critical: FDE-007 R1-N and R1-N-W are two parameter variations of **one** family
   (`M4_OBS_CORRIDOR`), not two independent families.
7. **Maturity** — no evidence-based 0–4 levels; no rule preventing failed/inconclusive experiments
   from raising success confidence.
8. **FDE integration** — no capture step that references original FDE files and hashes them.
9. **Continuous expansion** — no immediate post-append retrievability or growth metrics.

## 5. Risks and protected boundaries

- Never overwrite or delete historical records, baseline runs, failed runs or FDE reports.
- Never modify `benchmark/`, `runs/`, `experiments/`, `tools/`, `configs/`,
  `state/approval_policy.json`, the approval validator or the runner.
- Never weaken approval gates, DRC rules, D-007 evidence policy, scratch isolation or D-014.
- Never claim a PASS without artifacts and checksums; never treat `NOT EVALUATED` as PASS/FAIL.
- Avoid a duplicate KB: do not create a second log system, database, service or framework.
- Avoid generalizing design-specific SRAM/M4 geometry to other designs without validation.
- Beware stale documentation (e.g. `PROJECT_STATE.md` still referenced pre-approval R1-N text at
  audit time) — verify against artifacts, not prose.

## 6. Minimal integration plan (implemented)

| Phase | Implementation | Status |
|---|---|---|
| 0 Audit | This document; direct inspection; Agent G seed inventory | DONE |
| 1 Architecture | Standalone `scripts/sattva_kb.py` + `knowledge/` ledger; no new infra | DONE |
| 2 Knowledge model | Schema v1, provenance hashes, maturity, append-only `KBStore`, `verify` | DONE |
| 3 Retrieval | Deterministic decomposed factors, `search`, `explain` | DONE |
| 4 Applicability | `assess` with hard gates and declared remedy family | DONE |
| 5 Investigation integration | Query JSONs + `assess` before any recommendation; workflow documented | DONE |
| 6 Knowledge capture | `add` / `seed` with validation, duplicate check, FDE hashes | DONE |
| 7 Experiment history | `duplicate_check` family/variation/suppression; metrics repeated families | DONE |
| 8 FDE integration | 18 reviewed seed records from FDE-003..FDE-007, D-013/D-014, policies | DONE |
| 9 Testing | 20 offline tests in `tests/test_kb.py` + existing 25/25 and 14/14 regressions | DONE |
| 10 Independent audit | Agents B–F review (schema, retrieval, workflow, safety, validation) | IN PROGRESS |
| 11 Final adjudication | Resolve findings, publish, final evidence-based report | PENDING |

### Explicitly not built
No database, ORM, web service, REST API, embeddings, hosted-model call, automatic EDA execution,
automatic production promotion, DRC waiver, new approval policy, or modification to any existing
runner/approval module. The KB is a deterministic, offline, append-only memory layer.

## 7. Verification evidence (at audit implementation point)

- `sattva_kb.py` compiles under WSL Python 3.12; CLI subcommands available.
- `tests/test_kb.py`: 21/21 PASS (20 required scenarios + 1 diagnostic-not-remedy guard).
- `verify`: 18 records, zero integrity problems; append chain 18/18 links verified.
- `verify-immutable`: 9/9 protected artifacts OK (production LEF/GDS/Lib, config, SDC, approval
  policy, approval validator, runner, AGENTS.md).
- `metrics`: 18 records; `M4_OBS_CORRIDOR` = `[KB-0015, KB-0016]` (one family, two variations);
  `historical_baseline_available = false`.
- Worked decisions: DRT-0305 → STRONG_MATCH citing KB-0002; DRT-0073 → PREVIOUSLY_FAILED citing
  KB-0015 and KB-0016; broad-carve production proposal → INCOMPATIBLE.
