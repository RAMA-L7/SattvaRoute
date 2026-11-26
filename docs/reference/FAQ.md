# FAQ

Status: concise answers; authoritative details are linked. No marketing claims.

## What is SattvaRoute?
An evidence-driven physical-design diagnosis and controlled recovery framework for VLSI implementation workflows. `docs/product/PRODUCT.md`.

## Is it an AI tool?
It is a deterministic orchestration/diagnosis framework with an **optional, advisory** model path. No live-AI recovery is claimed; without credentials the advisory path is `SKIPPED_NO_CREDENTIALS`/`BLOCKED`. `docs/security/INPUT_AND_AI_RISKS.md`.

## Does it fix designs automatically?
No. It proposes bounded corrections; a human must create an approval; recovery is isolated and stage-limited. `docs/architecture/RECOVERY.md`.

## Does it guarantee routing/timing/signoff?
No. Flow completion ≠ timing closure ≠ coverage ≠ characterized timing ≠ signoff. Router DRC=0 ≠ foundry DRC. Timing ≠ functional correctness. `docs/engineering/VERIFICATION_BOUNDARIES.md`.

## Which design/PDK is validated?
Only `nangate_macro_control` (Nangate45 + `fakeram45_64x32` abstract macro) on pinned ORFS revision `25b6429c…` with two local patches and pinned tool hashes. `docs/reproducibility/BENCHMARK.md`.

## What about the 1000 ns vs 1 ns issue?
Historical `constraint.sdc` (1000 ns) is preserved; the 1 ns correction (`constraint_1ns.sdc`) was explicitly approved and applied after `report_units`/Liberty evidence established the 1000× error. `docs/engineering/SDC_TIMING.md`, `docs/TIMING_AUDIT.md`.

## What is the status of DRT-0073 / OpenFinRAM?
Unresolved, preserved, excluded. It is not reopened or relabeled. `docs/research/LIMITATIONS.md`.

## How do I run tests?
`python3 -m unittest discover -s tests -p 'test_*.py'` (157 test methods defined in `tests/test_*.py`, counted in this milestone). Prior records report the suites passing; not re-executed here (no Python interpreter). No credentials or flow run required. `docs/workflow/GETTING_STARTED.md`.

## Is there a chance my change will be applied without approval?
No path in the documented CLI applies a patch without an approval record that passes `sattva_approval.py validate`. `docs/security/SAFETY.md`.

## Can I use another foundry PDK or macro?
Not validated. The manifest pins one active profile; other profiles are declared/inactive. `docs/reference/CONFIGURATION.md`.

## How is licensing handled?
MIT covers original SattvaRoute code/docs only; third-party tools, PDKs, and collateral have separate terms and are not vendored. `LICENSE`, `docs/governance/LICENSING.md`, `docs/governance/THIRD_PARTY.md`.

## Where do I report a security issue?
Privately per `SECURITY.md`. Do not open a public issue for an unfixed vulnerability.

## Related

`docs/DOCUMENTATION_INDEX.md`, `docs/product/NON_GOALS.md`, `docs/research/LIMITATIONS.md`.
