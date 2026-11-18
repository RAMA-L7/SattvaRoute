# D-014 (PROPOSED — approval required): DRT-0305 recovery by marking `zero_` SPECIAL in the executed mirror before `pin_access`

- **Decision ID:** D-014 (new — does NOT overwrite D-013)
- **Status:** PROPOSED / **AWAITING APPROVAL** — not applied
- **Task:** T-M1-004 (Milestone 1C-R)
- **Proposed:** 2026-11-18T22:39:01+05:30
- **Supersedes:** D-013 (retained in the record as a FAILED execution attempt, not erased or relabeled)

## 1. Root cause being addressed

`zero_` is a logical constant-zero tie net created by OpenROAD's Verilog reader for the raw `4'h0` / `2'h0` literals on macro `u_sram` SIGNAL input pins (`sdel[3:0]`, `A[3:2]`). Because `SYNTH_NETLIST_FILES` short-circuits Yosys (`synth_preamble.tcl:34`), the normal `hilomap` tie-cell insertion (`synth.tcl:301–304`) never runs. `dbReadVerilog.cc:768–773` types the constant net as `GROUND` but never calls `setSpecial()`.

Consequently `4_cts.odb` contains `zero_` with `sigType=GROUND, isSpecial=0`. At `5_1_grt`, `pin_access` → DRT `io::Parser::addNet()` (`drt/src/io/io.cpp:1040`) evaluates `!is_special && getSigType().isSupply()` → true → DRT-0305. The PDN ground `VSS` is correctly `GROUND, isSpecial=1`; it is not implicated.

## 2. Supporting evidence

| Source | Evidence |
|---|---|
| Agent A (`reports/agent_A_orfs_execution_path.md`) | Runner sources the mirror `/mnt/d/SattvaRoute/tools/...` (`stage_route.log:1,17,55`); mirror git-clean at every run start (`preflight.txt:7`); no `set_special_nets` in 12 echoed command streams. |
| Agent B (`reports/agent_B_zero_net_database_trace.md`) | `zero_` present from `1_synth.odb`; `sigType=GROUND isSpecial=0`, 0 BTerms / 6 ITerms on `u_sram` signal pins, no shapes; `VDD`/`VSS` special=1. |
| Agent C (`reports/agent_C_special_net_mechanism.md`) | DRT-0305 guard source at `io.cpp:1040–1047`; `set_special_nets` absent from source/ORFS/binary; special status set via `add_global_connection -power/-ground` → `setSpecial()` (`OpenRoad.tcl:407–413`); `zero_` mis-typed at `dbReadVerilog.cc:768–773`. |
| Agent D (`reports/agent_D_independent_failure_analysis.md`) | `zero_` is the design's only driverless net (`RSZ-0020 found 1 floating nets`); `set_special_nets` → `invalid command name`; PDN/DB consistency confirmed. |
| Orchestrator read-only probe (2026-11-18T22:39:01+05:30) | On `4_cts.odb`: `[ord::get_db_block] findNet zero_` → net; `$net setSpecial` → `rc=0`, `isSpecial` 0→1; `$net setSigType SIGNAL` → `rc=0`. Confirms the in-memory object-method primitive is callable in this build. |

## 3. Exact modification (one logical change)

**Target file (execution mirror ONLY):** `D:\SattvaRoute\tools\OpenROAD-flow-scripts\flow\scripts\global_route.tcl`
**`D:\tools\OpenROAD-flow-scripts\flow\scripts\global_route.tcl` must NOT be touched** (read-only source of truth, per D-010/D-003).

**Location:** inside `proc global_route_helper { }`, immediately before `log_cmd pin_access {*}$additional_args` (currently line 66). Must precede the first DRT call.

Before:
```tcl
  append_env_var additional_args VIA_IN_PIN_MAX_LAYER -via_in_pin_top_layer 1

  log_cmd pin_access {*}$additional_args
```

After:
```tcl
  append_env_var additional_args VIA_IN_PIN_MAX_LAYER -via_in_pin_top_layer 1

  # D-014: zero_ is a constant-tie net that OpenROAD's Verilog reader typed
  # GROUND without the SPECIAL bit required by TritonRoute (DRT-0305).
  # Mark only this net SPECIAL before the first DRT call (pin_access).
  set d014_zero_net [[ord::get_db_block] findNet zero_]
  if {$d014_zero_net ne "NULL"} {
    $d014_zero_net setSpecial
  }

  log_cmd pin_access {*}$additional_args
```

- No RTL / netlist / macro / SDC / floorplan / placement / routing-layer / design-parameter changes.
- No other net is touched; the `findNet zero_` guard is a no-op if the net is absent.
- The command is an OpenDB object method (`$net setSpecial`), **not** the nonexistent `set_special_nets`.
- `log_cmd` echoes the two `set` lines but executes them directly — visible in the run's echoed command stream for verification.

## 4. Expected behavior

- `pin_access` no longer raises DRT-0305 (`zero_` now `isSpecial=1`; DRT places it in the special-net container).
- Global routing (`5_1_grt`) proceeds to completion; a `5_1_grt.odb` / route guide is produced.
- Downstream detailed routing, parasitic extraction, and final timing reports become reachable.

## 5. Side effects and residual risk (disclosed, not hidden)

- `zero_` remains a GROUND-typed, geometry-less special net. Its six macro SIGNAL input sinks are still not physically tied to `VSS` by the PDN. Detailed routing may report opens / DRC violations on those pins. **This fix unblocks global routing; it does not prove engineering correctness of the tie.**
- The `setSpecial` operation mutates only the in-memory DB during the route stage; it does not change the persistent `4_cts.odb` on disk.
- No effect on `VDD`/`VSS`, clock nets, constraints, or placement.

## 6. Affected files / stages

| Item | Value |
|---|---|
| Files modified | 1: mirror `flow/scripts/global_route.tcl` |
| `D:\tools` | untouched |
| Design files | untouched |
| Stages affected | `5_1_grt` only (before `pin_access`) |
| Original baseline | `runs/orfs_baseline_20261118T152845Z` — untouched, immutable |

## 7. Rollback

`git -C D:\SattvaRoute\tools\OpenROAD-flow-scripts checkout -- flow/scripts/global_route.tcl`
(or delete the 5 inserted lines). Hash before: `3968898c9abd8c0fd56c50d08bed6d3943bdc641f63c8674817449bbec2706ce`.

## 8. Verification plan (report-level, per D-007)

1. Record before/after sha256 of the mirror script; confirm `D:\tools` copy hash unchanged.
2. New unique run ID `orfs_baseline_d014_YYYYMMDDTHHMMSSZ` via `scripts/run_baseline_orfs.sh`.
3. Confirm `evidence/preflight.txt` shows `orfs_mirror_status` non-empty (patched), and `stage_route.log` shows the mirror path plus the echoed D-014 lines.
4. Confirm no DRT-0305; confirm `5_1_grt` rc=0 and route ODB/guide artifacts exist in the new run.
5. Continue: detailed routing → parasitic extraction → final timing reports; capture status, violations, unavailable checks.
6. If DRT-0305 persists or a new failure appears: STOP, preserve the failed run, do NOT apply a second speculative fix, analyze separately.

## 9. Required approval

**This proposal is NOT applied.** Approval is required before any edit or flow run. Approval must explicitly authorize:
- the one-line-equivalent `setSpecial` insertion in the mirror `global_route.tcl`, and
- the controlled recovery run with a new unique run ID.

D-013 remains recorded as a FAILED execution attempt.

---

## 10. Controlled experiment result (executed 2026-11-18T17:17:12Z)

**Approval:** granted by user (option "Approve D-014 + controlled run") before any edit or run.

**Applied:** exact §3 diff to the execution mirror only.
- Mirror hash before: `3968898c9abd8c0fd56c50d08bed6d3943bdc641f63c8674817449bbec2706ce`
- Mirror hash after: `cd86b58724f6c401b40d2cb464118d86590fa86b60cbe953eb4de53514d08099`
- `D:\tools` copy unchanged: `3968898c…` (git-clean); new run `preflight.txt` shows `orfs_mirror_status: [ M flow/scripts/global_route.tcl]`.
- Original baseline `stage_route.log` sha256 unchanged: `2dd7a167bb9eb54ab2a0164cd83deb4f2340bd17299a8d9c34b469ece0e1f35d`.

**Run ID:** `runs/orfs_baseline_20261118T171712Z` (unique; runner-generated ID).

**Result — PARTIAL / new blocker:**
- **DRT-0305 RESOLVED.** `5_1_grt.log` no longer contains DRT-0305. Design import reports `Number of snets: 3` (was 2) and `Number of nets: 72` (was 75), confirming `zero_` was reclassified SPECIAL and moved into the special-net container.
- **New failure:** `[ERROR DRT-0073] No access point for u_sram/clk (sram_x4x4x1).` at `pin_access` (`5_1_grt.log:108`; source `drt/src/pa/FlexPA_acc_point.cpp:1524–1533` — zero generated access points for the instance term). Preceded by `[WARNING DRT-0419] No routing tracks pass through the center of Term u_sram/D[0..3]` and `Q[0..3]`.
- Route stage still rc=2; no `5_*.odb` and no `route.guide` produced. Detailed routing / extraction / timing remain NOT EVALUATED.

**Decision per task directive §7:** STOP. No second speculative fix applied. DRT-0073 is a distinct macro pin-access issue requiring its own analysis and a new decision ID with fresh approval.

**Status:** D-014 APPLIED; DRT-0305 FIX VERIFIED; global routing still BLOCKED by a different cause. Not a completion claim.
