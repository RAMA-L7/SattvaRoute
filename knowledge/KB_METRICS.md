# Knowledge Base measurement (actual, 2026-11-23)

Measured from `/mnt/d/SattvaRoute` in WSL Ubuntu-24.04. No values are estimated.

## Growth / state

| Metric | Actual value |
|---|---|
| Total records | 18 |
| Outcome distribution | PASS 6, FAIL 6, BLOCKED 5, INCONCLUSIVE 1 |
| Scope distribution | REUSABLE 16, DESIGN_SPECIFIC 2, CROSS_DESIGN 0 |
| Maturity histogram | L0 4, L1 2, L2 10, L3 2, L4 0 |
| Reuse-linked records | 1 (`KB-0016` → `KB-0015`) |
| Repeated families | `DIAGNOSTIC_BUILD` ×3, `DIAGNOSTIC_ROOT_CAUSE` ×2, `M4_OBS_CORRIDOR` ×2 |
| Integrity verification | PASS, 18/18 records, 0 problems; append chain 18 links verified |
| Protected artifact check | PASS, 9/9 unchanged |
| Immutable manifest SHA-256 | `c6b2a49d71bc57bd3713bbb6647341d2afd4e666af8a9d128cca750f37bbf035` |
| Provenance check | DRIFT: 42 hashes checked, 16 differences, all from the single legitimate D-024 append to `docs/decisions/DECISIONS.md` (see `PROVENANCE_DRIFT.md`) |

`M4_OBS_CORRIDOR` ×2 is **one** remedy family with two parameter variations (FDE-007 R1-N and
R1-N-W), not two independent families or two confirming experiments.

## Retrieval latency (wall clock, 10 CLI invocations each)

| Operation | 10 runs | Per run | Max RSS |
|---|---|---|---|
| `assess` | 1.84 s | ~0.18 s | ~20 MB |
| `search` | 2.05 s | ~0.21 s | ~20 MB |

Python interpreter startup dominates; the KB itself is in-memory JSONL with 18 records.

## Tests (actual)

| Suite | Result |
|---|---|
| `tests/test_kb.py` | 21/21 PASS (20 required scenarios + 1 diagnostic-not-remedy guard) |
| `tests/test_approval.py` (regression) | 25/25 PASS |
| `tests/test_runner.sh` (regression) | RESULT: PASS=14 FAIL=0 |

## Historical comparison unavailable

`historical_baseline_available = false`. There is no pre-KB record of investigation time, retrieval
time, candidate counts, experiments per investigation, duplicate rate, reuse rate or success rate.
This measurement point is the baseline for future comparison; earlier values are **not**
reconstructed or invented.

## Interpretation limits

- Cross-design reuse rate is 0 by construction: no second design exists in this project and no
  maturity-4 record can be justified.
- The single reuse link is a documented negative-family link, not a validated reuse.
- A high score is an applicability signal, never proof of physical correctness.
