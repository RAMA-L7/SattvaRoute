# CLI reference

Status: all commands verified against `scripts/pnr_cli.py`, `scripts/sattva_approval.py`, `scripts/manifest.py`, `scripts/verify_run.py`, `scripts/diagnosis_agent.py`, `scripts/evaluate_diagnosis*.py`, `scripts/live_diagnosis.py`, `scripts/remedy_kb.py`, `scripts/remedy_engine.py`, `scripts/timing_audit.py`, `scripts/evidence_package.py`.

## Primary entry point — `scripts/pnr_cli.py`

| Command | Required args | Optional args | Behavior |
|---|---|---|---|
| `status` | — | — | Manifest check + control path + approval-gate reminder |
| `baseline` | — | `--tag` | Run control baseline; `engineering_verdict: NOT EVALUATED` |
| `failure-demo` | — | `--tag` | Create attempt-local missing-Liberty fixture; originals untouched |
| `diagnose` | `--run` | `--out` | Deterministic classification + optional advisory model note |
| `live-diagnose` | `--bundle` | `--gt`, `--raw-out`, `--out` | Advisory model call; no apply/approve/execute |
| `propose` | `--diagnosis`, `--target` | `--baseline`, `--mirror`, `--out` | Bounded unapplied patch; `PENDING_HUMAN` or `NO_PROPOSAL` |
| `approve-view` | `--proposal` | — | Display exact diff, hashes, risks, verification criteria |
| `resume` | `--approval`, `--patch`, `--design-root`, `--source-run`, `--source-run-id`, `--decision-id` | `--tag` | Validate approval, then apply + stage-limited rerun |

## Approval service — `scripts/sattva_approval.py`

| Command | Arguments |
|---|---|
| `create` | `--approval-id`, `--decision-id`, `--source-run-id`, `--patch`, `--target`, `--earliest-stage`, `--rerun-scope`, `--approver`, `--design-root`, `--policy`, `--out`; optional `--status APPROVED\|REJECTED`, `--note`, `--candidate-id`, `--expected-final-hash`, `--expires-at`, `--profile` |
| `validate` | `--approval`, `--patch`, `--policy`, `--design-root`, `--run-id`; optional `--decision-id`, `--for-apply` |
| `apply` | `--approval`, `--patch`, `--policy`, `--design-root`, `--evidence-dir` |
| `guard` | `--approval`, `--patch`, `--policy`, `--design-root`, `--run-id`, `--evidence-dir`; optional `--decision-id` |
| `check-source-artifacts` | `--approval`, `--policy`, `--source-work`; optional `--results-root` |

## Manifest — `scripts/manifest.py`

`--manifest`, `--root`, `--profile`, `--mirror`, `--check`, `--fingerprint`, `--no-git`, `--list-profiles`, `--design-root`.

Common: `python3 scripts/manifest.py --check --profile nangate_macro_control --mirror <orfs>`

## Verification — `scripts/verify_run.py`

`--run`, `--audit`, `--baseline`, `--failure`, `--recovery`, `--audit-map`, `--approval-apply`, `--targeted-marker`, `--out`.

```
python3 scripts/verify_run.py --run <run> [--audit <audit.json>]
python3 scripts/verify_run.py --baseline B --failure F --recovery R --audit-map <audits.json> --approval-apply <A.json>
```

## Diagnosis — `scripts/diagnosis_agent.py`

Subcommands `classify --run [--out]`, `propose --diagnosis --target [--baseline] [--mirror] [--out]`.

## Evaluation

- `evaluate_diagnosis.py`: `deterministic --bundle [--out]`, `grade --output --bundle --gt [--out]`.
- `evaluate_diagnosis_v2.py` (frozen): `grade --output --bundle [--gt] [--out]`.
- `evidence_package.py`: `--out` (default curated bundle path).

## Live model — `scripts/live_diagnosis.py`

`config` (redacted provider config), `call --bundle --prompt [--raw-out]`.

## Timing — `scripts/timing_audit.py`

`--run`, `--platform`, `--macro-lib`, `--out`; optional `--openroad`.

## Remedy KB / engine

- `remedy_kb.py`: `init`, `append --record`, `verify [--expected-head]`, `retrieve --query [--type --limit]`, `refuted [--signature]` (all with `--ledger`).
- `remedy_engine.py`: `rank --candidates [--kb-records --signature-hint --budgets]`.

## Tests

```
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Non-commands

There is no `fix`, `auto-repair`, `signoff`, `approve-now`, or `--force-approve` command. Do not invent CLI options.

## Related

`docs/reference/CONFIGURATION.md`, `docs/workflow/WORKFLOW.md`, `docs/reference/STATUS_CODES.md`.
