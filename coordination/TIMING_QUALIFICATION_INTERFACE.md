# Timing Qualification Adapter — shared interface (authoritative for this milestone)

## Files owned

- Agent A: `scripts/audit_timing.tcl`, `scripts/timing_audit.py`, `scripts/timing_qualification.py` (new)
- Coordinator: `scripts/verify_run.py`, `tests/test_timing_qualification.py`, `config/timing_tolerances.json`, docs
- No agent edits `evaluate_diagnosis_v2.py`, RTL, SDC, benchmark collateral, or historical evidence.

## Capability contract

- Legacy `update_timing` must be removed from mandatory checks.
- Supported API: `::sta::find_timing -full_update` (confirmed in pinned OpenROAD).
- Emit `CAPABILITY_AVAILABLE sta_find_timing` on success; `CAPABILITY_UNAVAILABLE` + `SECTION_UNSUPPORTED TIMING_UPDATE` when absent.
- Missing/uninvokable capability -> `UNKNOWN`, never PASS.

## Qualification record `timing_qualification/v1`

Path produced by adapter: `evidence/timing/<prefix>_qualification.json` with raw stdout at `<prefix>_qualification.raw.txt`.

```json
{
  "schema": "timing_qualification/v1",
  "run_id": "string from evidence/run.json",
  "active_profile": "string from SATTVA_DESIGN_PROFILE",
  "binding": {
    "design_fingerprint": "canonical manifest.py fingerprint (not the manifest file digest)",
    "orfs_revision": "git HEAD of mirror",
    "opensta_revision": "submodule commit if recoverable, else UNKNOWN",
    "sdc_sha256": "...",
    "liberty_std_sha256": "...",
    "liberty_macro_sha256": "...",
    "rc_set_sha256": "...",
    "rcx_rules_sha256": "...",
    "spef_sha256": "...",
    "odb_sha256": "...",
    "tool": {"id":"openroad","version":"bazel-nostamp","exe_sha256":"...","invocation":"..."},
    "raw_output_sha256": "..."
  },
  "capability": {"id":"sta_find_timing","invocation":"::sta::find_timing -full_update","available":true,"rc":0,"status":"AVAILABLE|UNAVAILABLE|UNKNOWN"},
  "metrics": {"wns":0.0,"tns":0.0,"worst_slack_max":0.64,"worst_slack_min":0.08,"clock_period":1.0,"timing_paths":1,"unconstrained_paths":0,"unannotated_drivers":0,"partially_unannotated_drivers":0},
  "status": "PASS|UNKNOWN|FAIL"
}
```

## Verifier requirements

Reject: wrong run ID, wrong tool hash, wrong profile, canonical fingerprint mismatch, changed SDC/Liberty/RC/SPEF/ODB hashes, tampered raw output hash, non-finite metrics. Missing capability -> UNKNOWN. Numeric baseline/recovery comparison uses `config/timing_tolerances.json`; tolerances were frozen before requalification.

## Requalification evidence naming

New runs only; original PR #4 evidence remains untouched:
- baseline: `orfs_baseline_tq_baseline_*`
- failure: `orfs_baseline_tq_failure_*`
- recovery: `orfs_baseline_tq_recovery_*`
