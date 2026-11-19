# Milestone 1 Assessment — SattvaRoute

> **HISTORICAL / POINT-IN-TIME — SUPERSEDED (2026-11-19).** This document records an earlier assessment and is retained for history. Do not read its status statements as current. Corrections: DRT-0305 was subsequently **eliminated by D-014**; the current blocker is **DRT-0073** (`u_sram/clk` pin access); no `5_1_grt.odb` has ever been produced, so the instruction below to inspect one is invalid; the decision ledger now reaches D-014, not D-012; `app/` has **0 files**, so no dashboard/backend/worker exists; and the claimed persistence/cancellation/resume machinery did not exist at that time (see `docs/architecture.md` and `PROJECT_STATE.md`). FDE-001/FDE-002 later added runner reliability and approval enforcement — see `logs/REPORT_LOG.md`.

## Official Assessment (as recorded)

> Milestone 1: Benchmark integration and reproducible baseline infrastructure completed. Baseline PnR partially successful. Floorplan, placement, and CTS verified. Detailed routing remains blocked by DRT-0305. Engineering completion remains pending successful routing, extraction, and final timing evaluation.

This distinction matters. Your orchestration infrastructure has made progress, even though the physical-design flow has not yet reached its final endpoint.

## Recommended Next Phase

### Milestone 1C: Routing Investigation and Baseline Completion

**Prioritize:**

1. **Investigate DRT-0305 using actual routing logs and generated database evidence.**
   - Examine `stage_route.log` from `runs/orfs_baseline_20261118T152845Z/evidence/`
   - Inspect the `5_1_grt.odb` and related routing database artifacts
   - Review the `0_*` through `5_*` stage logs for context

2. **Identify whether the failure originates from:**
   - Special-net geometry (net `zero_` not routable by TritonRoute)
   - Macro pin access constraints (M3/M4 pin arrangements from sram_x4x4x1)
   - PDN interactions (vdd/vss on M3 with M5/M6 grid connections)
   - Routing constraints (TritonRoute layer/direction/pitch settings)
   - Tool/platform limitation (WSL2, memory 7.6 GiB, OpenROAD bazel-nostamp)

3. **Develop the smallest evidence-supported correction.**
   - Make exactly one change at a time
   - Record each change with run ID, timestamp, and before/after state
   - Do not change multiple routing variables simultaneously

4. **Record the proposed change before applying it.**
   - Use the approval workflow established in the project
   - Document the patch identity, affected stage, and expected effect

5. **Require approval.**
   - Follow the existing approval service pattern from the project

6. **Run a new baseline attempt with a unique run ID.**
   - Incremental run numbering from existing `runs/orfs_baseline_*`

7. **Verify detailed routing.**
   - Check for DRT errors, routing violations, congestion

8. **Continue into parasitic extraction and final timing reports**
   - Where the configured flow supports them
   - Distinguish execution completion from engineering checks passing

9. **Preserve the existing failed baseline as immutable evidence.**
   - Do not overwrite `runs/orfs_baseline_20261118T152845Z/`
   - New runs get new timestamps

**Do not:** Change multiple routing variables simultaneously. A reproducible baseline and a clear causal relationship between fix and result are required.

## Final Milestone Evidence (to be completed)

Your next completion report should include:

- [ ] Baseline and recovery run IDs
- [ ] Routing failure root cause
- [ ] Approved fix and configuration diff
- [ ] Detailed routing status
- [ ] Parasitic extraction status
- [ ] Final setup and hold metrics
- [ ] Routing violations
- [ ] Congestion metrics, if available
- [ ] Runtime and peak memory
- [ ] Unsupported or unavailable checks
- [ ] Honest engineering verdict

## Current Status

- ✅ Foundational benchmark and integration work complete
- ✅ Three failure cases diagnosed and recovered (missing .lib, illegal macro location, invalid routing-layer)
- ✅ Orchestration infrastructure in place (stage execution, persistence, cancellation, resume)
- ✅ Dashboard infrastructure partially built (app/backend/frontend/worker)
- ⚠️ Routing blocker DRT-0305 remains — next priority
- ✅ Evidence collection and logging infrastructure complete
- ✅ DECISIONS.md records D-001..D-012

## Immediate Next Step

Investigate the DRT-0305 error from the existing baseline run, develop the smallest evidence-supported correction, and run a new baseline attempt.