# T-WORKFLOW-001 — DRT-0073 Workflow Demonstration

**No EDA was run. No remedy was tested. No fix is claimed.**

## 1. Reuse instead of re-diagnosis

The engine's DIAGNOSIS stage consumed the existing attribution:
- signature `DRT-0073 No access point for u_sram/clk`;
- fixed M4 OBS abs `(4704,16560)-(4764,16584)`, Short cid0/rid48;
- source `docs/ENG013_BLOCKER_ATTRIBUTION.md` (reused, not rerun).

The remedy KB sidecar supplied tool context (build fingerprint `a77fc27`, binaries, tech LEF), five research sources with URLs and applicability predicates, eight refuted families, and the baseline/treatment metrics from ENG011/ENG012.

## 2. Ranking and automatic elimination

`scripts/run_remedy_demo.py` evaluated ten candidate families. Result:

| Candidate | Score | Status | Reason |
|---|---|---|---|
| C-BROAD (broad carve) | 0.7475 | eliminated | previously refuted (illegal: 120+92 real shapes) |
| C-GEN (generator OBS regeneration) | 0.665 | **selected, then gated** | legality UNVERIFIED |
| C-HAND (narrow carve) | 0.5663 | eliminated | previously refuted (0 APs; 12 nm new edge) |
| C-Y (y envelope) | 0.5613 | eliminated | previously refuted |
| C-OBSSEM (OBS SPACING / USEMINSPACING) | 0.4617 | eliminated | source-proven predicate mismatch |
| C-EXT (extended west carve) | 0.3925 | eligible but below threshold | GDS vacancy/all-pin unknown |
| C-CONFIG / C-FILTER / C-PLACE / C-PIN | 0.24–0.36 | eliminated | previously refuted |

## 3. Selection outcome

The strongest eligible candidate (`C-GEN`, score 0.665) was blocked by the legality gate:

```
stages = FAILURE, DIAGNOSIS, RESEARCH, RANK, SELECT, SANDBOX(skipped), VALIDATE(skipped), REPORT
selection = null
gated_candidate = C-GEN
stop_condition = RISK_EXCEEDS_POLICY
unresolved_gap = C-GEN: legality unverified, prerequisites=
  generator configurability proof, GDS vacancy per pin, all-pin AP,
  full-flow signoff, fresh approval
execution_state = NOT_RUN
eda_executed = false
kb_write = engineering_conclusion record WF-RUN-DRT0073-001 appended
```

This is the desired behavior: the engine selects a candidate, refuses to sandbox it without legality evidence, and emits an actionable research gap instead of an unverified fix.

## 4. Evidence artifacts

- `experiments/WF-DEMO/T-WORKFLOW-001/remedy_demo.json` — full machine-readable report (stage checkpoints, refuted families, ranked components, stop condition).
- `knowledge/remedy_ledger.jsonl` — 22 hashed records (21 seeded + run outcome), verify PASS, head `a32f41d5…`.
- `scripts/run_remedy_demo.py` — reproducible command: `python3 scripts/run_remedy_demo.py`.

## 5. What the demonstration proves

1. Prior evidence is retrieved and reused; root cause is not restarted.
2. Web/KB sources are attached with URLs and applicability predicates.
3. Refuted remedies are eliminated automatically before ranking.
4. Ranking is deterministic and decomposable.
5. The legality gate stops an otherwise top-ranked candidate.
6. No EDA, no geometry, no production change, no false success claim.

It does **not** prove that a fix exists or that the engine can execute one; execution requires a separately authorized harness and a candidate that passes the legality gate.
