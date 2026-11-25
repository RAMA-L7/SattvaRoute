# T-PNR-001 — Tests Actually Run

## Offline suites (credential-free)

| Suite | Command | Result |
|---|---|---|
| Remedy engine + KB | `python3 -m unittest discover -s tests -p 'test_remedy_*.py' -v` | 33 tests PASS (after all controller changes) |
| Approval | `python3 -m unittest discover -s tests -p 'test_approval.py' -v` | 30 tests PASS |
| KB | `python3 -m unittest discover -s tests -p 'test_kb.py' -v` | 21 tests PASS |
| Runner | `bash tests/test_runner.sh` | PASS=14 FAIL=0 |
| Manifest | `python3 scripts/manifest.py --check` | PASS (21 declared files hashed) |
| Integrity | `python3 scripts/sattva_kb.py verify ...`, `remedy_kb.py verify` | KB 19/19 PASS; sidecar 22 records, chain PASS |

New coverage added: stage-entry vs total timing, hard-expiry blocking before execution, invalid transitions, unselected/repeated/post-stop execution, timeout preservation of measured PASS, approval binding (candidate/profile/expiry/final hash/env paths), context-scoped and kind-scoped refutations, concurrent KB writers, corrupted/interrupted writes, reconsideration.

## Live EDA attempts

Recorded under `runs/orfs_baseline_*`. Each has `evidence/preflight.json`, `manifest.json`, `stages.tsv`, `jobs.jsonl`, `artifact_sha256.txt`, per-stage logs and `run.json`. Engineering verdicts are separate from RC.

| Attempt | Design | RC | Finding |
|---|---|---|---|
| `riscv32i_control_20261125T135901...` | upstream `asap7/riscv32i` | 2 | Synth blocked: installed Yosys 0.33 cannot read ASAP7 `SEQ_RVT_FF` Liberty (`Missing function on output IQ`); ORFS script also uses unsupported `-setattr`. Preserved as failed feasibility evidence. |
| `fakeram_control_20261125T140125...` | upstream `asap7/riscv32i-mock-sram/fakeram7_256x32` | 2 | Same ASAP7 Liberty/Yosys incompatibility. Preserved as failed feasibility evidence. |
| `nangate_macro_control_20261125T144339456871595Z_11464` | Nangate45 + platform `fakeram45_64x32` wrapper | 0 | **Baseline ACCEPTED**: all 8 stages rc=0; routed ODB, `6_final.spef`, `6_final.def`, `6_final.gds`, `6_finish.rpt`, `5_route_drc.rpt` present; DRC report has 0 violations; setup/hold/slew/fanout/cap violation counts 0; TNS/WNs 0.00; worst slack 899.75 ns at 1000 ps. |
| `failure_20261125T145821Z_20261125T145821234238490Z_20208` | attempt-local config with invalid macro Liberty reference | 2 | Controlled failure: synth stopped on missing `missing_fakeram45_64x32.lib`. Fixture `experiments/PNR-RECOVERY/missing_macro_lib_20261125T145821Z/`. Original benchmark untouched. |
| `recovered_final_20261125T152826305943439Z_27610` | same attempt with approved patch `RESTORE_MACRO_LIB` | 0 | Recovery endpoint reached: 6 approved stages (`synth…finish`) rc=0 in 325 s, routed ODB/SPEF/final reports present, empty DRC report with `DRT-0199 violations=0`, setup/hold/slew/fanout/cap counts 0. Approval `AP-PNR-003`, operation `3205f326…`, patch SHA-256 `8a7178f6…`. |

## Controlled failure and proposal

- Deterministic diagnosis: `family=MISSING_MACRO_LIB`, failed stage `synth`, RC 2, evidence refs in `diagnosis.json`.
- Exact patch proposal: `proposal.json`, candidate `RESTORE_MACRO_LIB`, patch SHA-256 `8a7178f6d1c7eb6fb8fb0d815da1e79f07d01f47441d986c40cc2c0abba419cc`, status `PENDING_HUMAN`.
- Model note: unavailable (`SATTVA_MODEL_URL` not configured); diagnosis is deterministic, not a simulated live-model response.

No original ORFS design/platform file was modified. One execution-mirror `synth.sh` was accidentally overwritten by a shell-quoting error and restored immediately from the read-only upstream tree; no EDA result depended on the overwritten content (see `IMPLEMENTATION_GAPS.md`).

## Not run / open

- Live model diagnosis (no `SATTVA_MODEL_URL` configured): acceptance item remains open; deterministic classification was used.
- External DRC/LVS signoff: outside scope. ORFS `finish` produced GDS and internal reports only.
