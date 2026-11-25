# T-PNR-001 — Verified Gap List and Corrections

Sources: read-only audits `IMPL_A_runner_approval.md`, `IMPL_B_controller_kb.md`, `IMPL_C_benchmark.md`; direct coordinator verification.

| # | Gap (verified) | Reference | Correction implemented |
|---|---|---|---|
| G1 | Per-stage elapsed used global controller age, not stage entry | `remedy_engine.py:133-148` | `BudgetTracker.enter_stage`, separate `stage_elapsed` and total `elapsed`; monotonic clock preserved |
| G2 | Hard expiry did not block execution; terminal states not enforced | `_stage`, `sandbox_and_validate` | `_assert_active`, `VALID_TRANSITIONS`, `_assert_can_execute`, terminal stop; pre-execution expiry guard |
| G3 | No process timeout/cancellation in runner | runner stage loop | `timeout --signal=TERM --kill-after=30`, `jobs.jsonl`, `trap on_signal`, `cancellation.json` |
| G4 | Timeout erased a valid measured PASS during reporting | `report()` | Execution outcome and report outcome separated; `EXPIRED_AFTER_MEASUREMENT` flag; no erasure |
| G5 | Any candidate could be executed; repeated execution allowed | controller | selection + diagnosis + attempt guards; persisted state and interruption reconciliation |
| G6 | Refutation blacklisting ignored context and conflated kinds | `remedy_kb.refuted_families` | context-scoped refutations, 6-kind taxonomy, `reconsider()` append-only record, family aliases |
| G7 | Boolean-only authorization | `authorized: bool` | `sattva_approval.validate_approval` binding (approval ID, run ID, candidate, patch hash, profile, expiry, final hash); legacy shim documented |
| G8 | PASS trusted self-reported flags | controller | evidence bar requires artifacts, metrics, checksums, reviewer, baseline/treatment refs |
| G9 | Remedy KB append was unlocked/racy | `remedy_kb.append_record` | shared `TargetLock` + in-process lock around read→verify→duplicate→append with fsync |
| G10 | KB manifest refresh outside lock | `sattva_kb.cmd_add` | `update_manifest` inside `TargetLock`; write-time verify added |
| G11 | Approval guard ran before preflight | runner `:73-78` | moved after preflight; failed preflight never touches the mirror |
| G12 | Source-run identity unchecked | runner `:182-186` | `run.json.run_id` compared with approval `source_run_id` |
| G13 | Dependency artifacts checked only by existence | approval `:480-491` | SHA-256 check against source `artifact_sha256.txt` |
| G14 | Hard-coded machine paths in policy | policy `:5,:31` | `$SATTVA_ROOT` expansion with project-root default |
| G15 | No shared dependency manifest | absent | `config/sattva_manifest.json` + `scripts/manifest.py`, wired into runner preflight and run evidence |
| G16 | No CLI/backend/UI | `app/*` empty | `scripts/pnr_cli.py` single CLI entry point; no broad UI work |
| G17 | No diagnosis agent | absent | `scripts/diagnosis_agent.py`: deterministic parser + bounded proposal, optional provider-configurable model note |
| G18 | `validated_at` second-boundary race | approval `:458-465` | comparison ignores `validated_at` |
| G19 | Resume duplicated EDA stages | runner | `SATTVA_RESUME_DIR` skips successful stages, seeds validated results, no duplicate jobs |
| G20 | `app/backend` etc. empty | verified | documented CLI-first scope; no services added |

## Protected-artifact manifest refresh

The immutable manifest lists the runner, approval tool and approval policy as protected. This task explicitly authorized hardening those files. Their hashes were refreshed in `knowledge/kb_immutable_manifest.json` with `captured_at=2026-11-25T00:00:00+00:00`; design data (`benchmark/design/sattva_sram/*`, macro LEF/GDS/LIB, SDC), AGENTS.md and R2 were not changed. The hash chain remains an integrity mechanism, not immutable storage.

## Incident (recorded for transparency)

During a shell-quoting mistake, the execution mirror copy `tools/OpenROAD-flow-scripts/flow/scripts/synth.sh` was overwritten with a shell transcript at 2026-11-25T14:02:54+00:00. It was restored immediately from the read-only upstream `D:\tools\OpenROAD-flow-scripts` and verified by SHA-256 (`210A863C…`). No original upstream file, design input, LEF/GDS/lib, config, or production artifact was changed. The two failed ASAP7 feasibility runs predate the incident and their synth logs are genuine.
