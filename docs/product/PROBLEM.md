# Problem statement

## Engineering problem

Physical-design implementation failures are difficult to diagnose and safely correct because:

1. **Failures are distributed** across stage logs, reports, generated SDC, manifests, Liberty/LEF collateral, config, and run artifacts; no single message is the root cause.
2. **Error messages describe symptoms**, not root causes (e.g. `No rule to make target …needed by 1_synth.odb`).
3. **Dependency and configuration ambiguity**: attempt-local overrides, multiline declarations, multiple library paths, `$(…)` constructs; effective value ≠ declared value; original vs overridden.
4. **Timing-unit mistakes**: bare numbers require knowing tool `report_units`/Liberty `time_unit`; historical 1000 ns vs documented 1 ns **1000×** error; CTS `updated_clks.sdc` ≠ executed final.
5. **Incorrect or missing collateral**; macro/corner must match pinned platform; no invented replacements.
6. **Failure propagation across stages**; earliest affected stage → downstream invalidation.
7. **Stale or missing reports**; empty report ≠ clean; `rc=0` ≠ engineering pass; early `DRT-0199=0` then final nonzero; missing-in-both.
8. **Incomplete verification**: flow completion ≠ timing closure ≠ coverage ≠ characterized timing ≠ signoff; router DRC=0 ≠ foundry DRC; timing ≠ functional correctness.
9. **Risky corrective changes**: broad edits, unsafe substitution, corner change, constraint relaxation, approval reuse, hash mismatch, stale fingerprint, cross-run contamination.
10. **Repeated reruns without a validated hypothesis**; no isolated recovery; no correlation between diagnosis and applied change.
11. **Poor reproducibility**: original state not preserved; tool revision + local patches + tool binary + collateral hashes not verified; historical results rewritten.
12. **AI unsafety**: prompt injection in logs; model-generated unsafe patches; no evidence binding; no human gate.

## Why this matters

These problems increase **debugging time, engineering effort, risk of unsafe change, and uncertainty**, and undermine **reproducibility and trust**. In VLSI, an incorrect belief about units, collateral, corner, or completeness can lead to wasted iterations or unsafe corrections.

## Related

`docs/product/PRODUCT.md`, `docs/engineering/PHYSICAL_DESIGN.md`, `docs/engineering/FAILURE_TAXONOMY.md`, `docs/security/THREAT_MODEL.md`.
