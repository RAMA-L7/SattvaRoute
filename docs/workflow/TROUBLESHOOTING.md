# Troubleshooting

Status: failure-handling guidance. Do not "fix" by relaxing constraints, swapping corners, or inventing collateral. Record engineering issues as recommendations, never silently change production files in this documentation milestone.

## Preflight fails

Symptom: `manifest.py --check` mismatch. Likely causes: ORFS HEAD not at pinned revision; working tree contains changes beyond the two declared patches; tool binary hash mismatch; collateral hash mismatch; wrong `SATTVA_MIRROR`. Response: reacquire pinned checkout, apply the two local patches declared in `config/sattva_manifest.json` (the runner-generated `evidence/mirror.patch` is not published), rebuild/point pinned tool binaries. Do not bypass preflight.

## Diagnosis says `insufficient_evidence` / `NO_PROPOSAL`

Meaning: no bounded rule matches the evidence. Response: provide more evidence (logs, resolved config), inspect `evidence_refs`, or escalate to a human decision. Do not force a proposal.

## Verification reports `UNKNOWN` or `FAIL` on missing evidence

Meaning: a required report/log is absent or unreadable. Response: check the run's `evidence/` and `work/reports/`. An empty report is not clean without completion evidence. Do not relabel as PASS.

## DRT count confusion

The verifier reads the **last** DRT-0199 count in the routing log. Intermediate counts (25 → 2 → 0) are expected; do not diagnose from the first count. Absence of report lines is not "zero violations".

## Timing numbers look wrong

Read `report_units` and Liberty `time_unit` before interpreting periods. If a 1000 ns period appears, consult `docs/engineering/SDC_TIMING.md` and `docs/TIMING_AUDIT.md`; the historical 1000× error was resolved by tool evidence, not by editing reports. `updated_clks.sdc` is intermediate, not final.

## Live AI unavailable

`SATTVA_MODEL_URL` unset or provider error → `SKIPPED_NO_CREDENTIALS` / `BLOCKED`. This is expected. Deterministic diagnosis still works; no live-AI recovery is claimed. See `docs/security/INPUT_AND_AI_RISKS.md`.

## Recovery verdict not "fixed"

Check verification: regressions vs baseline, missing evidence, or inconclusive reports. A successful patch application or `rc=0` is not a fix. Review `docs/HELDOUT_RECOVERY.md` for a correctly executed example.

## DRT-0073 / OpenFinRAM

Unresolved and preserved. Do not reopen. See `docs/research/LIMITATIONS.md`.

## Reporting a problem

Include run ID, stage, verbatim log excerpt, tool versions, the exact command, and which evidence you inspected. Separate observation from hypothesis. See `CONTRIBUTING.md` and `SUPPORT.md`.

## Related

`docs/architecture/FAILURE_STATES.md`, `docs/reference/STATUS_CODES.md`, `docs/REPRODUCIBILITY.md`.
