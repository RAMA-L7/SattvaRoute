# SattvaRoute Incremental Engineering Knowledge Base

- **Mission:** incremental, evidence-grounded, reusable engineering memory.
- **Implementation:** `scripts/sattva_kb.py` (Python 3, standard library only).
- **Storage:** `knowledge/` — append-oriented JSON Lines ledger plus derived manifest.
- **Design principle:** FDE reports remain the **authoritative investigation history**; the KB is a
  pointer-and-evidence index that becomes the **reusable memory** across investigations. It does not
  rewrite, replace or reinterpret historical FDE evidence.

## 1. What exists and what is reused

SattvaRoute already had a working memory system (`PROJECT_STATE.md`, `coordination/`, `logs/`),
a deterministic approval boundary (`scripts/sattva_approval.py`) and a hardened runner
(`scripts/run_baseline_orfs.sh`). The KB adds only the missing structured capability: typed records,
provenance hashes, transparent retrieval, applicability decisions, duplicate suppression and FDE
capture. It reuses the approval module's cross-process lock (`TargetLock`) and the JSONL/atomic-write/
SHA-256/strict-validation pattern rather than introducing a database, framework, service or network
dependency.

No EDA is executed by the KB. No flow input, design artifact, production file, binary, baseline or
approval policy is modified.

## 2. Storage layout

| Path | Purpose | Mutability |
|---|---|---|
| `knowledge/kb_records.jsonl` | One JSON object per line; the KB ledger | **Append-only**. Never edited or deleted. |
| `knowledge/kb_chain.json` | Append hash chain: record count + chained SHA-256 | Appended atomically with each record; detects deletion/reordering |
| `knowledge/kb_manifest.json` | Derived counts, histograms, repeated families, store hash | Regenerated on write (derived, not historical). |
| `knowledge/kb_immutable_manifest.json` | SHA-256 of protected artifacts captured at init | Written once at `init`. |
| `knowledge/fde_seed.json` | Reviewed FDE-to-record extraction used by `seed` | Append source; existing IDs are skipped. |
| `knowledge/queries/*.json` | Example failure queries for demonstration/regression | Read-only inputs. |

A correction is a **new** record with a higher `record_version` and `relationships.supersedes`
pointing at the prior ID. The prior line is never touched.

## 3. Record structure (schema version 1)

Each record contains:

- **Identity/provenance:** `knowledge_id`, `record_version`, `created_at`, `identity`
  (`investigation_id`, `fde_id`, `experiment_ids`, `design_id`, `design_fingerprint`, `source_run`,
  `timestamp`), `provenance` (`fde_records`, `source_hashes` with actual SHA-256 of each FDE file,
  `captured_at`), and `integrity.record_sha256` over the canonical record.
- **Failure characteristics:** `failure` (`category`, `signature`, `violation_type`, `tool`,
  `tool_version`, `technology`, `geometry`, `routing_layers`, `constraints`, `environment`, `pvt`,
  `logs`, `reports`, `metrics`).
- **Hypothesis/root cause:** `root_cause` (`status` ∈ ESTABLISHED/PROBABLE/REFUTED/UNKNOWN,
  `hypothesis`, `supporting_evidence`, `contradicting_evidence`, `confidence`,
  `alternative_explanations`, `unresolved_questions`).
- **Remedy:** `remedies[]` (`remedy_id`, `remedy_family`, `description`, `exact_modifications`,
  `preconditions`, `compatibility`, `expected_outcome`, `risks`, `side_effects`, `outcome`).
- **Experiment:** `experiment` (`experiment_id`, `baseline_reference`, `scratch_environment`,
  `exact_changes`, `tool_invocation`, `configuration`, `execution_status`, `reproducibility`,
  `estimated_cost`).
- **Outcome:** `outcome.state` ∈ **PASS / FAIL / INCONCLUSIVE / BLOCKED / NOT_RUN**.
- **Applicability:** `applicability` (`scope` ∈ DESIGN_SPECIFIC/REUSABLE/CROSS_DESIGN, `conditions`,
  `validated_characteristics`, `limitations`, `exclusions`, `compatible_environments`,
  `cross_design_reuse`).
- **Evidence:** `evidence` with explicitly separated `observations`, `hypotheses`, `inferences`,
  `experimentally_supported`, `validated_knowledge`, `checksums`, `before_after`,
  `reviewer_findings`.
- **Relationships/maturity:** `relationships` (`related_ids`, `duplicate_of`, `supersedes`,
  `remedy_family`), `maturity` 0–4.

### Enforced rules

- `PASS` is **rejected** unless `experimentally_supported` or `validated_knowledge` is non-empty
  **and** checksums or reports are cited. Success is never inferred from missing evidence.
- `FAIL` / `INCONCLUSIVE` / `BLOCKED` / `NOT_RUN` cannot be assigned maturity ≥ 3.
- Maturity 4 requires `cross_design_reuse = validated` plus related cross-design records.
- A `supersedes` correction requires `record_version >= 2` and must reference an existing record.
- An executed experiment cannot claim a production design/baseline path as `scratch_environment`.
- Unknown fields, wrong enums and malformed records are rejected before append.
- `verify` recomputes every record hash, revalidates every line, checks the append chain and the
  derived store hash; tampering, deletion and reordering are detectable.
- A finding/diagnostic family (root-cause, candidate diagnostic, build, evidence policy, vocabulary,
  runner validation) is **never recommendable as a remedy**, even with a PASS outcome.

## 4. Commands

All commands require `--store knowledge/kb_records.jsonl --knowledge-root knowledge` (except
`init`, `verify-immutable`).

```bash
# one-time initialisation (captures protected artifact hashes)
python3 scripts/sattva_kb.py init --knowledge-root knowledge --project-root .

# append FDE-derived records (existing IDs skipped; append-oriented)
python3 scripts/sattva_kb.py seed --store knowledge/kb_records.jsonl \
  --knowledge-root knowledge --seed-file knowledge/fde_seed.json --fde-root .

# rank historical cases (factors are returned per case)
python3 scripts/sattva_kb.py search --store knowledge/kb_records.jsonl \
  --knowledge-root knowledge --query knowledge/queries/drt0073_pin_access.json

# applicability decision BEFORE any remedy recommendation
python3 scripts/sattva_kb.py assess --store knowledge/kb_records.jsonl \
  --knowledge-root knowledge --query knowledge/queries/drt0305_zero_net.json

# duplicate / family-variation check for a proposed experiment
python3 scripts/sattva_kb.py duplicates --store knowledge/kb_records.jsonl \
  --knowledge-root knowledge --record <new-record.json>

# integrity, immutability, provenance and growth metrics
python3 scripts/sattva_kb.py verify --store knowledge/kb_records.jsonl --knowledge-root knowledge
python3 scripts/sattva_kb.py verify-immutable --manifest knowledge/kb_immutable_manifest.json \
  --project-root .
python3 scripts/sattva_kb.py verify-provenance --store knowledge/kb_records.jsonl \
  --knowledge-root knowledge --fde-root .
python3 scripts/sattva_kb.py metrics --store knowledge/kb_records.jsonl --knowledge-root knowledge
```

A query may declare `remedy_family` and `exact_modifications`. This lets the engine evaluate a
specific proposed family against **all** prior records, not only the top-ranked case. A
reconsideration of a failed family must supply **both** `new_justification` and
`new_evidence_refs`; free-form text alone cannot bypass suppression. `chain-init` is a one-time
migration to create the append chain for an existing ledger.

## 5. Retrieval and ranking

`search()` returns decomposed, inspectable factors (no opaque similarity):

| Factor | Weight | Meaning |
|---|---|---|
| `failure_similarity` | 0.28 | Token coverage of failure signature/violation, with exact violation-code bonus |
| `root_cause_similarity` | 0.16 | Overlap of root-cause hypothesis/status |
| `compatibility` | 0.20 | Technology, layers, tool and design fingerprint compatibility |
| `evidence_quality` | 0.10 | Breadth of evidence plus checksums |
| `validation_history` | 0.06 | Maturity / 4 |
| `success_history` | 0.04 | Presence of a verified PASS precedent |
| `applicability_conditions` | 0.10 | Match of documented conditions to current context |
| `experiment_cost` | 0.06 | Prefer cheaper diagnostics when otherwise equal |
| `risk_level` | −0.08 | Penalty for documented risks/side effects |
| `failure_history` | −0.04 | Penalty for prior failure (record stays searchable) |

`assess()` then applies **hard gates before recommendation**: no signature overlap →
`NO_RELEVANT_KNOWLEDGE`; documented exclusion match → `INCOMPATIBLE`; insufficient evidence or
`NOT_RUN` → `INSUFFICIENT_EVIDENCE`; previously failed family without new justification →
`PREVIOUSLY_FAILED`; design-specific evidence for a different design → `PARTIAL_MATCH`; only then can
a high-scoring PASS precedent yield `STRONG_MATCH`. Every decision returns a `trace` of record IDs
and record hashes. Similarity is never treated as proof of applicability.

## 6. Duplicate detection and suppressed experiments

`duplicate_check()` classifies a proposed experiment against prior records as:
`exact_duplicate` (same signature, family, design fingerprint and modification digest),
`parameter_variation` (same family/design/signature, different modification), or `related_family`.
An exact violation-code match counts as comparable even when signature prose differs.

A prior `FAIL` in the same family under comparable conditions **suppresses** a retry unless
`new_justification` is supplied; with justification the decision is downgraded to `PARTIAL_MATCH`
and controlled validation is required — never an automatic STRONG_MATCH.

**FDE-007 correctness:** `R1-N` (`KB-0015`) and `R1-N-W` (`KB-0016`) are recorded as TWO parameter
variations of the **single** remedy family `M4_OBS_CORRIDOR`, both `FAIL`. They must never be counted
as two independent remedy families or as two confirming experiments.

## 7. Knowledge maturity

| Level | Meaning | Enforced interpretation |
|---|---|---|
| 0 | Hypothesis / failed or blocked attempt | No success confidence; negative evidence only |
| 1 | Observed, single-source or reviewed requirement | Not validated |
| 2 | Validated in one specific design/environment (or one controlled negative experiment) | Ceiling for a single experiment |
| 3 | Replicated / convergent multi-agent + multi-experiment evidence, bounded scope | Only with independent review |
| 4 | Cross-design validated under compatible conditions | Not reached in this project; no signoff evidence exists |

Failed and inconclusive experiments never raise success confidence. No record in the current KB is
level 4.

## 8. FDE integration and continuous expansion

For each completed FDE, extract failure, hypotheses (including rejected), root-cause status, remedies
and families, experiments, outcomes, side effects, evidence, limitations and uncertainty. Record
these in `knowledge/fde_seed.json` (or a future per-FDE seed file) with `provenance.fde_records`
pointing to the original reports. Run `seed` to append. The originals are never altered; the KB
stores their SHA-256 at capture time.

After each investigation: collect verified results → check evidence completeness → separate fact
from interpretation → classify design-specific vs reusable → check duplicates/relations → assign
maturity → append → run `verify` → confirm the new record is retrievable via `search`. New knowledge
is available immediately after append (no rebuild or index service).

## 9. Safety

- All KB writes are confined to `knowledge/` by `assert_safe_write()`.
- Protected artifacts are hashed at init and checked by `verify-immutable`.
- The KB never runs EDA, applies patches, changes approval policy, suppresses DRC, waives violations
  or promotes anything to production.
- The existing approval gates and runner are untouched and still mandatory for any flow change.

## 10. Known limitations

- Retrieval is deterministic lexical/field matching with explicit weights. No embeddings or learned
  ranking are used; no hosted model or network access.
- `design_fingerprint` is currently a curated string (`sattva_sram/sram_x4x4x1@asap7`), not an
  automatically computed hash of all design inputs.
- No historical time/cost baseline exists; `metrics` sets `historical_baseline_available=false` and
  measurement starts from this point. Investigation time, reuse rate, duplicate rate and success
  rate cannot be retroactively fabricated.
- Cross-design reuse is compatibility-aware but unproven across designs (maturity 4 unreachable).
- `PDN-0006` appears in no inspected source and is therefore not seeded as an observed violation.
- Provenance hashes are point-in-time. `docs/decisions/DECISIONS.md` legitimately changed after
  capture (decision D-024 was appended), so `verify-provenance` currently reports `DRIFT` for that
  one source. See `knowledge/PROVENANCE_DRIFT.md`. No FDE report changed.
- The immutable manifest lives inside the writable KB root; its SHA-256 is recorded in the derived
  manifest and repeated in published evidence so out-of-band changes are detectable.
- Publication uses `scripts/publish_kb.sh` with an explicit allowlist, blocklist and post-copy
  SHA-256 verification; no run/ODB/GDS/binary artifacts are copied.
