# T-PNR-001 — Reproducible Recovery Workflow

## Entry point

`scripts/pnr_cli.py` is the single CLI. All runs are isolated under `runs/orfs_baseline_<tag>_<stamp>_<pid>/`; nothing overwrites an earlier run.

```
python3 scripts/pnr_cli.py status
python3 scripts/pnr_cli.py baseline --tag control
python3 scripts/pnr_cli.py failure-demo
python3 scripts/pnr_cli.py diagnose --run <failed-run-dir> --out experiments/PNR-RECOVERY/diagnosis.json
python3 scripts/pnr_cli.py propose --diagnosis experiments/PNR-RECOVERY/diagnosis.json \
    --target <attempt-local-config.mk> --out experiments/PNR-RECOVERY/proposal.json
python3 scripts/pnr_cli.py approve-view --proposal experiments/PNR-RECOVERY/proposal.json
```

`approve-view` prints the failure, supporting evidence, exact diff, expected effect, risks, affected stages and verification criteria. It does **not** create or consume an approval.

## Failure fixture

`failure-demo` creates an attempt-local config under `experiments/PNR-RECOVERY/missing_macro_lib_<stamp>/design/config.mk` with one deliberate change: `export ADDITIONAL_LIBS =` (the macro Liberty reference is omitted). Original benchmark configs, RTL, SDC, LEF/LIB/GDS, macro placement and technology rules are untouched. The fixture is declared by the implementation task, not by a recovery approval.

## Diagnosis and proposal

- `diagnose` parses actual `stages.tsv`/logs; it never infers success from RC 0.
- The classification is deterministic. If `SATTVA_MODEL_URL` is set, an optional OpenAI-compatible model note is attached and labelled; otherwise `model.available=false`.
- `propose` only emits an exact patch for the bounded `MISSING_MACRO_LIB` family. No generic or speculative fix is produced.
- The patch is a unified diff with SHA-256, original hash, candidate ID, affected stages, expected effect, risks and verification criteria.

## Approval gate (human)

The CLI stops. No patch is applied until the engineer creates an approval record through the existing service:

```
python3 scripts/sattva_approval.py create \
  --approval-id AP-... --decision-id D-... --source-run-id <failed-run-id> \
  --patch <proposal.patch.file> --target <attempt-local-config.mk> \
  --earliest-stage synth --rerun-scope synth,floorplan,place,cts,route,finish \
  --approver <name> --design-root <attempt-design-dir> \
  --policy state/approval_policy.json --out <approval.json> \
  --candidate-id RESTORE_MACRO_LIB --profile riscv32i_attempt \
  --expires-at <ISO-8601>
```

After explicit human approval of that exact operation:

```
python3 scripts/pnr_cli.py resume --approval <approval.json> --patch <patch> \
  --design-root <attempt-design-dir> --source-run <failed-run> \
  --source-run-id <failed-run-id> --decision-id D-...
```

The runner revalidates the approval after preflight, verifies source-run identity, applies only the approved diff, copies validated prerequisites, and reruns only the affected stages.

## Trust boundary

Local CLI approval is single-user only. It proves that an explicit approval record exists and binds the exact patch/operation; it does **not** provide enterprise identity verification or multi-user authorization.

## Verification

A recovery PASS requires: baseline/treatment artifacts and hashes, report contents, original failure condition absent, no new DRT codes, all-pin/route/DRC/timing/collateral checks as applicable, independent review, and protected-artifact parity. Error disappearance alone is insufficient.
