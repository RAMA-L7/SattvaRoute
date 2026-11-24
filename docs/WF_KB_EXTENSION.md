# T-WORKFLOW-001 — KB Extension and Retrieval Behavior

## 1. Extend, not replace

The authoritative `scripts/sattva_kb.py` ledger (`knowledge/kb_records.jsonl`, 19 records, chain PASS) is untouched. A new append-only sidecar `knowledge/remedy_ledger.jsonl` adds the structured record types the existing schema cannot express.

## 2. Record types (12)

`failure_signature`, `root_cause`, `tool_context`, `research_source`, `remedy_candidate`, `successful_fix`, `refuted_remedy`, `experiment_config`, `baseline_treatment_metrics`, `regression_result`, `resolution_time`, `engineering_conclusion`.

Every record: `record_id`, `type`, `created_at`, `payload`, `prev_hash`, `record_hash` (SHA-256 over canonical JSON). Duplicate IDs rejected; tampering detected by `verify`.

## 3. DRT-0073 seed

21 seeded records from ENG009–ENG015: signature, root cause, tool context, five cited research sources with applicability predicates, eight refuted remedy families, experiment config with baseline/control/positive-control and metrics/abort list, baseline/treatment metrics, regression state, resolution time, and final NO-GO conclusion. Seeded idempotently by `scripts/seed_remedy_kb.py`.

## 4. Retrieval

```
python3 scripts/remedy_kb.py retrieve --ledger knowledge/remedy_ledger.jsonl --query 'DRT-0073 OBS' [--type refuted_remedy]
python3 scripts/remedy_kb.py refuted --ledger knowledge/remedy_ledger.jsonl --signature 'DRT-0073'
python3 scripts/remedy_kb.py verify --ledger knowledge/remedy_ledger.jsonl
python3 scripts/remedy_engine.py rank --candidates <json> --signature-hint 'DRT-0073'
```

`retrieve` tokenises payload text, returns record IDs and hashes (traceable evidence). `refuted_families` returns only families whose payload outcome is REFUTED/FAIL/REJECTED/INCONCLUSIVE. `remedy_engine.kb_refuted_families` also reads the original KB's `remedies[].outcome` and evidence observations, so historical failures become machine-visible without editing old records.

## 5. Compatibility and integrity

- No existing record edited or deleted; historical reports preserved.
- `sattva_kb.py verify` still PASS 19/19; `verify-immutable` PASS 9/9; validator PASS 13/13.
- Sidecar verify PASS 22 records (21 seeded + one run outcome `WF-RUN-DRT0073-001`), head `a32f41d5…`.
- Only new files added under `knowledge/`, `scripts/`, `config/`, `tests/`, `docs/`, `experiments/WF-DEMO/`.

## 6. Behavior change

Previously a refuted remedy could be re-proposed because refutations lived in prose. Now the ranking engine automatically vetoes any candidate whose family appears in the refutation registry, before any experiment is designed. The DRT-0073 demonstration shows 8 of 10 candidates eliminated automatically.
