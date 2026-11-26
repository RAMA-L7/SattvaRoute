# Evaluation methodology

Status: describes implemented evaluation assets. Frozen rubric: `scripts/evaluate_diagnosis_v2.py`. Historical results are preserved in `docs/` and `T1_*` reports.

## Diagnosis evaluation

- **Frozen rubric:** `evaluate_diagnosis_v2.py` (v2) is frozen; `evaluate_diagnosis.py` retains deterministic/grade subcommands for earlier methodology.
- **Bundles:** `scripts/evidence_package.py` builds bounded evidence bundles; ground truth is kept separate from the bundle.
- **Grading:** `grade --output <out> --bundle <bundle> [--gt <gt>] [--out <result>]` compares a diagnosis output against the bundle and ground truth under the frozen rubric.
- **Deterministic path:** `evaluate_diagnosis.py deterministic --bundle <bundle>` grades rule-based classification without a model.
- **Live path:** `pnr_cli.py live-diagnose` can call a model and optionally grade; without credentials the call is `SKIPPED_NO_CREDENTIALS`/`BLOCKED` and is **not counted** as a successful AI evaluation.

## Recovery evaluation

Recovery is evaluated by independent verification (`verify_run.py --baseline B --failure F --recovery R ...`), not by the runner return code. A recovery is not a fix if verification shows regressions, missing evidence, or inconclusive reports. The held-out case (`docs/HELDOUT_RECOVERY.md`) is a correctly executed example: deterministic diagnosis → human-approved patch → isolated attempt → `verify_recovery` PASS.

## Protocol rules

1. Do not tune a rubric after seeing results; v2 is frozen.
2. Keep ground truth out of the diagnosis input bundle.
3. Separate deterministic and model-generated outputs in reporting.
4. Do not count absent credentials as success.
5. Preserve historical evaluations and verdicts (including rejected live runs) verbatim.

## Historical evaluations

`T1_EXPERIMENT_REPORT.md`, `T1_ADJUDICATION.md`, `T1_LIVE_R2_EXPERIMENT_REPORT.md` and related reports are preserved records of live-AI validation, including a `REJECTED` verdict. They are not relabeled here. See `docs/REPORT_INDEX.md`.

## Limitations

Single benchmark, small bundle set, no cross-design generalization claim, no quantified productivity/accuracy gain, no production signoff. See `docs/research/LIMITATIONS.md`.

## Related

`docs/reproducibility/BENCHMARK.md`, `docs/architecture/DIAGNOSIS.md`, `docs/security/INPUT_AND_AI_RISKS.md`.
