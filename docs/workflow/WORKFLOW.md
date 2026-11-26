# End-to-end workflow

Status: describes the implemented sequence; commands verified against source. Diagram: `docs/diagrams/RECOVERY_LIFECYCLE.md`.

## Overview

```
baseline → (failure) → evidence → diagnose → propose → approve-view
        → human approval → resume (isolated, stage-limited) → verify_run → verdict
```

## 1. Baseline execution

```
python3 scripts/pnr_cli.py baseline [--tag TAG]
```
Preflight runs first; stages execute with evidence capture. The CLI output status is process-level; engineering verdict is `NOT EVALUATED`.

## 2. Evidence collection

Evidence is captured automatically under `<run>/evidence/`. Review `run.json`, `stages.tsv`, `stage_*.log`, `preflight.txt`/`preflight.json`, `manifest.json`. See `docs/architecture/EVIDENCE.md`, `docs/reference/ARTIFACTS.md`.

## 3. Failure diagnosis

```
python3 scripts/pnr_cli.py diagnose --run <failed-run> [--out diagnosis.json]
```
Returns family, mechanism, `evidence_refs`, earliest affected stage, and downstream invalidation. Optional advisory model note is added by `optional_model_note`; it is not required for the deterministic result.

For an optional live advisory call:
```
python3 scripts/pnr_cli.py live-diagnose --bundle <bundle-dir> [--gt <ground-truth.json>] [--out <out.json>]
```
Without credentials the status is `BLOCKED`/`SKIPPED_NO_CREDENTIALS`; no patch/approval/execution occurs.

## 4. Proposal review

```
python3 scripts/pnr_cli.py propose --diagnosis <diagnosis.json> --target <target-file> [--baseline B] [--mirror M] [--out proposal.json]
python3 scripts/pnr_cli.py approve-view --proposal <proposal.json>
```
`propose` produces a textual, unapplied patch with exact diff, hashes, risks, and verification criteria; status `PENDING_HUMAN`. `NO_PROPOSAL` means no bounded rule applies — stop, do not invent a fix.

## 5. Human approval

A human inspects the exact diff and creates an approval record:
```
python3 scripts/sattva_approval.py create --approval-id <id> --decision-id <id> \
  --source-run-id <id> --patch <patch> --target <target> --earliest-stage <stage> \
  --rerun-scope <scope> --approver <name> --design-root <root> --policy state/approval_policy.json --out <approval.json>
python3 scripts/sattva_approval.py validate --approval <a> --patch <p> \
  --policy state/approval_policy.json --design-root <root> --run-id <id> [--decision-id <id>]
```
See `docs/architecture/APPROVAL.md`, `docs/security/SAFETY.md`.

## 6. Controlled recovery

```
python3 scripts/pnr_cli.py resume --approval <a> --patch <p> --design-root <root> \
  --source-run <run> --source-run-id <id> --decision-id <id> [--tag TAG]
```
`resume` validates approval first; the runner then applies the approved op and reruns from the earliest affected stage in an isolated attempt. Originals and baseline are preserved.

## 7. Independent verification

```
python3 scripts/verify_run.py --baseline B --failure F --recovery R \
  --audit-map <audits.json> --approval-apply <A.json> [--out <verdict.json>]
```
Produces the recovery verdict from report-level checks. Missing evidence fails; regressions are flagged. See `docs/architecture/VERIFICATION.md`.

## 8. Interpretation

Engineering validation is human: decide whether reports meet the design's goals. Do not claim signoff, timing closure, coverage, or functional correctness from these checks. See `docs/engineering/VERIFICATION_BOUNDARIES.md`.

## Related

`docs/workflow/GETTING_STARTED.md`, `docs/product/USE_CASES.md`, `docs/reference/CLI.md`.
