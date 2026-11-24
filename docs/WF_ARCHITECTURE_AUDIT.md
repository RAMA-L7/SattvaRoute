# T-WORKFLOW-001 — Architecture Audit

## 1. Scope

Read-only audit of agents, skills, workflow, KB, experiment framework, approval policy and project state. Sources: `sattva_kb.py`, `sattva_approval.py`, `run_baseline_orfs.sh`, `tests/*`, `.skills/*`, `docs/ENG009–ENG015`, `knowledge/*`, `PROJECT_STATE.md`, and four role audits (Research, EDA Source, Physical Design, Validation).

## 2. Why investigations become prolonged

- **One decision ID per experiment.** FDE-004→007, ENG009→015 each required a fresh approval, 3–4 agents, independent review and adjudication. DRT-0073 spanned ~6 days (2026-11-18 → 11-24) (VERIFIED from dated reports).
- **Three sessions lost to diagnostic-build blockers** (FDE-006/006R/006S) before a usable instrumentation path existed.
- **Diagnosis was repeated** across milestones because results lived in prose reports, not retrievable structured records.
- **The KB stops at ENG010 (KB-0019).** ENG011–ENG015 refutations are prose-only and invisible to `sattva_kb.search`; `duplicate_check` cannot suppress a candidate refuted at source level but never executed (Agent R).
- **No resolution controller.** The runner enforces verification boundaries (run IDs, preflight, hashes, RC, approval ledger) but has no clock, state machine, refutation→ranking feedback, candidate cap, or machine-readable unresolved end state (Agent V).
- **R2 checklist is DRAFT/INACTIVE**, so available experimental discipline is not enforced.

## 3. Duplicate research and experiments

| Duplication | Evidence |
|---|---|
| Re-deriving the M4 OBS blocker geometry | ENG010 sliver, ENG011 arms, ENG012 forensics, ENG013 shape-level attribution |
| Re-testing narrow OBS corridors | R1-N, R1-N-W, C1, C2, exact-strip carve — all 0 APs |
| Re researching the same upstream fixes | ENG015 A/B/C each re-read the same PRs/issues; no shared source ledger |
| Replaying broad-carve ODB | FDE-006U, ENG012 replay, ENG013 replay |

## 4. Bottlenecks

1. **Diagnosis → research:** no structured handoff; each milestone restated the premise.
2. **Research → remedy:** no ranking function; agents produced lists, not a single actionable selection.
3. **Remedy → execution:** approval gate is correct but not paired with a time budget or automatic next-candidate advance.
4. **Result → memory:** negative results were written as reports, not queryable refutation records.

## 5. Existing capabilities to reuse (do not rebuild)

- `sattva_kb.py`: append-only hash-chained ledger, decomposed search scoring, six-class `assess`, `duplicate_check`, family/variation suppression, integrity + immutable + provenance verification (19/19 records, 9/9 protected).
- `sattva_approval.py`: exact-patch approval ledger, allowed roots, scope enforcement, reuse rejection, atomic patch applier with rollback.
- `run_baseline_orfs.sh`: collision-safe run IDs, blocking preflight, input/binary/patch fingerprinting, process RC propagation, `run.json`/`preflight.json`.
- `EXPERIMENT_DESIGN_CHECKLIST.md` R2 (advisory/inactive): A7 family check, A14 toolchain manifest, A17 capability preflight.
- ENG010 marker provenance dataset, ENG011 path-matched no-op control pattern, ENG012–013 ODB/instrumentation artifacts, ENG015 cited research set.

## 6. Missing capabilities implemented in this milestone

- Machine-readable **failure signature** and **refutation registry** (remedy KB sidecar, 21 seeded records).
- Deterministic **remedy ranking** with automatic refutation-family elimination (`remedy_engine.rank_candidates`).
- **Time-budget state machine** with injectable clock and useful unresolved report (`BudgetTracker`, `RemedyEngine`).
- **Legality gate** before selection: `UNKNOWN`/`FAIL` legality blocks selection and emits prerequisites.
- **Failed-attempt advance** to the next qualified candidate (`record_failure_and_advance`).
- Offline unit/integration tests (16 new tests).

## 7. Residual gaps (not implemented here)

- The engine does not execute EDA; a future authorized harness must implement `execute(candidate)` with isolation and approval.
- Web research remains agent-driven (HTTP 402 during ENG015); structured source ledger exists but no automatic fetcher.
- Family-alias normalization beyond exact family strings is limited; canonical family names are required in candidate records.
- No automatic full-flow signoff (route/DRC/extraction/timing/KLayout) — still a manual engineering gate.

## 8. Verdict

The project already has strong *verification* infrastructure but lacked a *resolution controller*. This milestone adds the controller layer without replacing or weakening existing governance.
