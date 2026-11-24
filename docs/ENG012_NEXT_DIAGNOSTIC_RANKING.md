# T-ENGINEERING-012 — Ranked Next Diagnostics

No experiment is launched by this milestone. Ranking is by information gain, cost, risk, reproducibility, and whether it resolves the ONE remaining ambiguity (blocking shape/DRC sub-check).

| Rank | Diagnostic | Info gain | Cost | Risk | Reproducibility | Verdict |
|---|---|---|---|---|---|---|
| 1 | Log per-direction `PLANAR-DRC clean` flags + aggressor **source type / layer / rect** for each marker on the narrow-carve DB (`r1n_ref` or C1), using the existing provenance instrumentation | **HIGHEST** — resolves exact DRC sub-check and blocking OBS rectangle vs other macro-owned M4 shape | low (log-only patch + rebuild + one replay) | low | high (binary/hashes/harness preserved) | **RECOMMEND** (requires new approval) |
| 2 | Minimal west-strip carve only (abs x 4704–4764 at y≈16572) with no-op control, if rank 1 confirms an OBS slab | high — tests smallest mechanism-specific geometry | low | medium (geometry proposal) | high | conditional on rank 1 |
| 3 | E-side-only carve control (abs x 4848–4902) | medium — isolates side asymmetry | low | medium | high | conditional |
| 4 | M5-OBS-only control | low — via Shorts already non-binding | low | low | high | not priority |
| — | Repeat y-corridor / corner tab / broad carve / via-in-pin config | none | — | — | — | **REJECT — refuted or already tested** |

## Recommended next experiment (design only)

**ENG012-DIAG-002 — per-direction DRC source forensics.** Single variable: added log fields. Control: existing provenance binary debug-off. Measurement: for each candidate, planar direction bits, `markers.empty()` result, and each marker's source object type/layer/rect. Acceptance: blocking rectangle identified; no silent re-run of geometry variants. R2 advisory shadow only; no activation.

Stop; explicit authorization required before any rebuild or replay.
