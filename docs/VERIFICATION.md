# Verification (Phase 5) — `scripts/verify_run.py`

Report-level verification, **separate from comparison and separate from
acceptance**. A return code is not acceptance; two identically incomplete runs
both fail. Stdlib-only, offline.

## Status vocabulary (uniform)

`PASS` / `FAIL` / `UNKNOWN` / `NOT_EVALUATED`.

- `PASS` only if every required check passes.
- `FAIL` if any check fails (including "nonzero violations with rc=0").
- `UNKNOWN` if evidence is missing or unrecognized (not zero violations).
- `NOT_EVALUATED` if not required / not performed.

**Missing evidence is never PASS.** An empty report is clean **only** when
supported by expected tool-completion evidence.

## Five independent questions

1. **execution** — every declared stage ran in *this* run directory, rc=0,
   stage logs present, `overall_rc==0`, `first_failed_stage==null`.
2. **artifacts** — endpoint products present and non-empty (not missing-in-both).
3. **report_freshness** — endpoint reports newer than the run start; stale
   reports from another attempt rejected. (No reports ⇒ `NOT_EVALUATED`, not
   PASS.)
4. **engineering checks** (separate):
   - **routing**: `stage_route.log`; identify the **last** `DRT-0199 Number of
     violations = N`; correlate with run; require route-completion marker;
     `final==0`; empty `5_route_drc.rpt` clean **only** if final count 0 and
     route completed; non-empty DRC contradicts; no summary ⇒ `UNKNOWN`. **Not
     full foundry DRC.** Do not take the first match.
   - **timing**: `6_finish.rpt`; require `setup=0`,`hold=0`,`worst slack≥0`,
     `period_min`, `tns/wns`; **numeric values require a timing-unit audit**
     (`--audit`) with `units.time`, corner, `clock.period`; missing/unrecognized
     format ⇒ `UNKNOWN`; executed clock must match recorded `clock_period.txt`.
   - **timing_coverage**: `check_setup` empty, `unconstrained_endpoints==0`,
     required `registers`, `clocks`. Missing ⇒ `UNKNOWN`.
   - **extraction**: `6_final.spef` present/non-empty; `RCX-0045 Extract N>0`;
     `unannotated_drivers==0`; actual `read_spef` in finish log; missing or
     unsupported ⇒ `UNKNOWN/FAIL`. (Separate **extraction-completion** vs
     **annotation-coverage** vs **timing-use**.) 
5. **evidence completeness** — `run.json`, `stages.tsv`, stage logs, artifacts,
   audit. 
6. **recovery outcome** (`verify_recovery`, separate) — see below.

## Routing details

Sequence example on accepted baseline: `DRT-0199 [164,40,25,2,2,0]`, final `0`.
Final relevant detailed-routing summary, not first. `5_route_drc.rpt` 0 bytes
clean **because** final count=0 + completion (`write_db`/`fillcell`). Non-zero
final violations with rc=0 ⇒ FAIL. Non-empty report + zero count ⇒ FAIL.

## Timing details

`6_finish.rpt` `setup/hold`, `worst slack`, `period_min`, `tns/wns`. Units
captured by `scripts/timing_audit.py` (`report_units`, Liberty `time_unit`,
corner, PVT, RC). `set_propagated_clock`. Require `check_setup` empty. A number
without unit/corner is `UNKNOWN`.

## Extraction details

`scripts/audit_timing.tcl` mirrors ORFS `6_report` ordering:
liberty→db→sdc→`setRC`→`read_spef 6_final.spef`. `report_parasitic_annotation`.
`RCX-0045`. `set_extraction_rules_file $RCX_RULES`. Provenance hashes for
`rcx_patterns.rules`, `setRC.tcl`, SPEF. A change to extraction rules
invalidates final-analysis results (manifest fingerprint).

## Recovery verification (`verify_recovery`)

On top of each run's `verify_run`, and baseline + failure + recovery triple:

- **approved_change_reached**: `approval_apply.json` `phase=applied|verified`,
  `after_sha256`, plus `approval_guard.json`; approved op reached executed
  config. (See `scripts/sattva_approval.py`.)
- **target_failure_cleared**: targeted marker/stage no longer present in
  recovery evidence.
- **downstream_scope**: every affected stage reran or was validly reused;
  `rerun_scope` contiguous, starts at `earliest_affected_stage`.
- **collateral_regression**: recovery passes every check baseline passes; no
  regression. `baseline overall != PASS ⇒ FAIL`. (Not blanket-reject every
  warning; classify expected diagnostics vs regressions.)
- **failure_is_real**: failure run must not itself pass; recovery must execute.

## Negative fixtures (`tests/test_verify_run.py`, 20 tests; offline)

- both runs missing endpoint artifacts
- early zero then final nonzero DRT
- last zero after early nonzero
- stale report from another attempt
- missing timing units
- unconstrained endpoints
- nonzero violations with rc=0
- timing violation with rc=0
- incomplete extraction / unannotated / zero-net
- missing finish report
- recovery marker still present / scope stage missing / no approval / broken
  baseline / failure-that-passes
- clean-run positive control

## CLI

```
python3 scripts/verify_run.py --run <dir> --audit <timing_audit.json>
python3 scripts/verify_run.py --baseline B --failure F --recovery R \
    --audit-map map.json --approval-apply A.json --targeted-marker <m> --out out.json
```

## What verification does NOT establish

Flow completion ≠ timing closure ≠ coverage ≠ characterized physical timing ≠
signoff. Router DRC=0 ≠ foundry DRC. Timing ≠ functional correctness.
