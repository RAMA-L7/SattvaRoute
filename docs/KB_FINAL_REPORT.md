# SattvaRoute — Incremental Knowledge Base Integration: Final Report

- **Task:** T-KB-001
- **Date:** 2026-11-23
- **Verdict:** **ACCEPTED WITH LIMITATIONS** — the incremental KB is implemented, seeded, tested and
  independently reviewed. No production, design, baseline, binary or flow-input was modified. No
  signoff or success claim is made for the still-blocked physical-design flow.

---

## 1. Executive summary

SattvaRoute previously had extensive engineering history (FDE reports, decisions, logs, runs,
experiments) but no structured, queryable memory. This mission added the smallest safe capability
that turns that history into reusable engineering knowledge: a standalone, standard-library-only
module (`scripts/sattva_kb.py`) with an append-only JSONL ledger in `knowledge/`. It reuses the
existing approval ledger's patterns (SHA-256, atomic writes, strict validation, cross-process lock)
and introduces no database, framework, service, network call or hosted model.

The KB starts with the knowledge the project already had: **18 evidence-grounded records** derived
from FDE-003–FDE-007, D-013/D-014, review findings and policy decisions. It grows by appending
records; historical lines are never edited or deleted. Retrieval ranks cases by transparent,
decomposable factors, and applicability is decided **before** any remedy is recommended.

## 2. Initial audit (Phase 0)

Direct inspection verified: publication repo clean at `35fe33c` (= remote); live repo on `master`
with uncommitted FDE records; source baseline `orfs_baseline_20261119T131025284719666Z_9263` with
ODB `35bff121…`; production LEF `f1c18877…`, GDS `12c56777…`, OpenROAD `c1b90e0a…`. No active
locks. Full audit: `docs/KB_AUDIT.md`.

**Existing capabilities reused:** runner evidence model (FDE-001, 14/14 tests); approval validator and
ledger (FDE-002, 25/25 tests); FDE decision/report/log system; scratch experiment isolation;
D-007 report-level evidence policy; `TargetLock` from `sattva_approval.py`.

**Gaps closed:** typed records with provenance; append-only integrity chain; transparent retrieval;
applicability decision engine; design-specific vs reusable classification; maturity 0–4; duplicate
experiment suppression; FDE capture; continuous retrievability; growth metrics.

## 3. Architecture changes and implementation

| Component | File | Purpose |
|---|---|---|
| KB module | `scripts/sattva_kb.py` | Schema v1, store, validation, chain, retrieval, applicability, dedup, capture, metrics, CLI |
| Publication guard | `scripts/publish_kb.sh` | Allowlist + blocklist + post-copy SHA-256 verification |
| Tests | `tests/test_kb.py` | 21 offline tests covering all 20 required scenarios plus a guard |
| Knowledge store | `knowledge/kb_records.jsonl` | Append-only records (18) |
| Integrity | `knowledge/kb_chain.json`, `kb_manifest.json`, `kb_immutable_manifest.json` | Chain, derived state, protected-artifact hashes |
| Seed/evidence | `knowledge/fde_seed.json`, `queries/*.json`, `KB_METRICS.md`, `PROVENANCE_DRIFT.md` | FDE extraction, example queries, measurements, drift disclosure |
| Documentation | `docs/KNOWLEDGE_BASE.md`, `docs/KB_AUDIT.md` | Operation manual and audit |
| Decision | D-024 in `docs/decisions/DECISIONS.md` | Adoption record |

No new database, framework, service, REST API, embedding model, orchestration engine or hosted-model
dependency. No existing runner, approval validator or policy file was modified.

## 4. Knowledge lifecycle (demonstrated)

New failure → characterization → KB search → retrieval → applicability → decision. `assess()`
contains the **only** branch that emits a remedy recommendation, and it is reached only after
signature-overlap, exclusion, evidence-quantity, family-suppression, design-specificity and
actionable-remedy gates. If no applicable knowledge exists, the result is `NO_RELEVANT_KNOWLEDGE`
or `INSUFFICIENT_EVIDENCE`, which triggers a new investigation. Future FDEs capture structured
records via `seed`, which appends and immediately makes them retrievable.

Outcome states are explicit: PASS, FAIL, INCONCLUSIVE, BLOCKED, NOT_RUN. A PASS is rejected unless
experimentally supported evidence plus checksums/reports are cited. Failed and inconclusive records
remain searchable but never increase success confidence.

## 5. Cross-design reuse and maturity

`design_fingerprint` and technology/layer/tool fields drive a compatibility factor. Design-specific
evidence for a different design yields `PARTIAL_MATCH` with an explicit "cross-design promotion
requires new validation" reason — never `STRONG_MATCH`. Maturity levels 0–4 are enforced: failed or
unvalidated outcomes cannot reach level 3; level 4 additionally requires validated cross-design
reuse and related cross-design records. Current distribution: L0 4, L1 2, L2 10, L3 2, **L4 0** —
correctly, because no design has ever produced routing/signoff evidence in this project.

## 6. Experiment history and duplicate suppression (critical FDE-007 invariant)

`duplicate_check()` classifies proposals as `exact_duplicate`, `parameter_variation` or
`related_family`. An exact violation-code match counts as comparable even when prose differs.
A prior FAIL in the same family under comparable conditions suppresses a retry unless the query
supplies **both** `new_justification` and `new_evidence_refs`; even then the decision is only
`PARTIAL_MATCH` requiring controlled validation.

**FDE-007 is encoded correctly:** `KB-0015` (R1-N, scratch LEF `a0e2ea7c…`, run `…_97829`) and
`KB-0016` (R1-N-W, scratch LEF `917e094e…`, run `…_99729`) are two **parameter variations of the
single remedy family `M4_OBS_CORRIDOR`**, both `FAIL`/REJECT, linked by `related_ids`. They are not
counted as independent families or confirming experiments. Metrics confirm
`repeated_families.M4_OBS_CORRIDOR = [KB-0015, KB-0016]`.

## 7. Multi-agent orchestration

Coordinator owned all writes and adjudication; seven read-only agents produced independent reports:
- **A** architecture audit (found version/supersedes and unknown-field gaps);
- **B** knowledge architecture (found append-chain, maturity-cap and provenance gaps);
- **C** retrieval adversarial review (found unreachable decision class, partial explanation);
- **D** investigation workflow (found diagnostic-as-remedy HIGH finding);
- **E** independent safety review (ACCEPT WITH LIMITATIONS; required publication controls);
- **F** validation adjudication (PASS WITH LIMITATIONS; verified all executable criteria);
- **G** FDE knowledge inventory (18 seed records with real hashes/run IDs).

All blocking findings were resolved in code and re-verified. No agent modified project files.

## 8. Safety status

- Immutable baseline protection: `verify-immutable` PASS, 9/9 protected artifacts (production LEF,
  GDS, Liberty, config, SDC, approval policy, approval validator, runner, AGENTS.md).
- Scratch isolation: records cannot claim production design/baseline paths as scratch environments.
- Write boundary: all CLI writes confined to a `knowledge/` directory; symlinks and traversal refused.
- No EDA execution, patch application, DRC suppression, waiver, auto-deployment or production
  promotion. No approval gate weakened.
- Publication: `scripts/publish_kb.sh` copies only an explicit text allowlist and refuses any
  run/ODB/GDS/binary artifact, with per-file SHA-256 verification after copy.

## 9. Validation results (actual)

| Check | Actual result |
|---|---|
| `tests/test_kb.py` | 21/21 PASS |
| `tests/test_approval.py` (regression) | 25/25 PASS |
| `tests/test_runner.sh` (regression) | `RESULT: PASS=14 FAIL=0` |
| KB `verify` | PASS — 18 records, 18-link chain, 0 problems |
| KB `verify-immutable` | PASS — 9/9 unchanged |
| KB `verify-provenance` | DRIFT — 42 hashes, 16 differences, all from one legitimate source |
| DRT-0305 query | `STRONG_MATCH` → KB-0002 (D-014 `setSpecial`), with limitations/risks/validation |
| DRT-0073 query | `PREVIOUSLY_FAILED` → KB-0015 + KB-0016 (one family) |
| Broad-carve production query | `INCOMPATIBLE` |
| Retrieval latency | ~0.18 s/assess, ~0.21 s/search (10 CLI runs each, Python startup dominated) |

## 10. Evidence references

- Module: `scripts/sattva_kb.py`; tests: `tests/test_kb.py`; publication guard: `scripts/publish_kb.sh`.
- Ledger and manifests: `knowledge/kb_records.jsonl`, `kb_chain.json`, `kb_manifest.json`,
  `kb_immutable_manifest.json` (SHA-256 `c6b2a49d…f035`).
- Seed/inventory: `knowledge/fde_seed.json`; Agent G inventory (temp report `KB_G_inventory.md`).
- Agent reports (temp): `KB_A_audit.md`, `KB_B_arch.md`, `KB_C_retrieval.md`, `KB_D_investigation.md`,
  `KB_E_safety.md`, `KB_F_validation.md`.
- Historical evidence: `docs/FDE-003…FDE-007*.md`, `docs/decisions/DECISIONS.md` D-013/D-014/D-022/
  D-023/D-024, `experiments/FDE-007/*/evidence/*`, `logs/REVIEW_LOG.md` R-011/R-012.

## 11. Limitations and remaining gaps

1. **Provenance drift:** all 16 differences come from `docs/decisions/DECISIONS.md` because D-024
   was appended after seeding. No FDE report changed; recorded in `knowledge/PROVENANCE_DRIFT.md`.
   Point-in-time hashes are preserved, never silently rewritten.
2. **No historical performance baseline:** investigation time, reuse rate, duplicate rate and
   success rate before this KB do not exist and were not invented. Measurement starts here
   (`knowledge/KB_METRICS.md`).
3. **Maturity 4 unreachable:** no second design and no signoff-quality artifacts exist.
4. **Lexical retrieval:** transparent weighted token/field matching, not embeddings; no hosted model.
5. **Curated fingerprint:** `design_fingerprint` is a reviewed string, not an auto-computed hash of
   all design inputs.
6. **Manual capture:** future FDE records must be authored in a seed file; no automatic extraction
   from prose reports.
7. **Physical-design outcome unchanged:** FDE-007 remains BLOCKED; DRT-0073 has no validated
   production remedy; global/detail routing, DRC, extraction and timing are NOT EVALUATED.

## 12. Next recommended phase

Use the KB at the start of the next FDE: characterize the failure, run `assess` against a declared
`remedy_family`, follow the traced evidence, validate only in isolated scratch, then append a new
record and re-run `verify`. Any new DRT-0073 geometry attempt still requires a **new decision and
approval** with marker provenance (`getSrcs()`), GDS census at the sliver and spacing bands, a
spacing/EOL mechanism, all-pin AP evidence, a canonical DB diff plus no-op control, and a full-flow
plan — none of which is authorized by this KB mission.

**No production promotion is authorized by KB output alone.**
