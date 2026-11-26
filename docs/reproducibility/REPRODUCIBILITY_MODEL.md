# Reproducibility model

Status: describes implemented manifest v2 and evidence model. Authoritative full detail: `docs/REPRODUCIBILITY.md`.

## Goal

Another engineer should be able to recreate the published control run from pinned inputs without author-specific paths or untracked files. This is a **design goal**, not a claim that another engineer has tested it.

## Dependency manifest (`config/sattva_manifest.json`, v2)

- **Profile-scoped:** `nangate_macro_control` resolves the exact design, platform, flow, extraction, and tool inputs it consumes. Inactive profiles (`riscv32i_sattva`, `sattva_sram`) are declared but never checked.
- **Pinned ORFS:** revision `25b6429c1644a8682852646bebf19ff164402c76`, `verify_revision: true`, two declared local patches with SHA-256 and reason (global_route.tcl DRT-0305 special-net gate; synth_stdcells.tcl Yosys compat gate).
- **Pinned collateral hashes:** Nangate45 platform `config.mk`, tech/macro LEF, standard-cell LEF, typical Liberty, `fakeram45_64x32.lib`, RCX rules, `setRC.tcl`.
- **Pinned tool hashes:** OpenROAD and Yosys expected SHA-256.
- **Declared vs captured:** declared expectations are kept separate from captured fingerprints; one canonical `fingerprint` is produced by `manifest.py`.

## Fingerprinting

`scripts/manifest.py --check --profile nangate_macro_control --mirror <orfs>` verifies HEAD, tracked changes (exactly the declared patches), collateral hashes, and tool hashes, then emits a canonical digest. The same resolved set is consumed by runner preflight, approval validation, resume, and evidence bundles. A mismatch fails closed.

## Baseline preservation

- Historical 1000 ns runs and reports are preserved; `constraint.sdc` is preserved verbatim.
- The 1 ns correction is a separate approved file (`constraint_1ns.sdc`) repointed from `config.mk`; the new baseline PASS is a new run, not a rewritten old one.
- Recovery attempts use isolated directories; originals and baselines are never modified in place.

## Commands (verified)

```
python3 scripts/manifest.py --check --profile nangate_macro_control --mirror <orfs>
python3 scripts/pnr_cli.py status
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Validation status

Author-run clean-environment validation only. Prior records report offline suites passing; 157 test methods are defined in `tests/test_*.py` (counted here) and were not re-executed in this shell. Verified baseline PASS via `verify_run.py`. No external independent reproduction claim.

## Related

`docs/REPRODUCIBILITY.md`, `docs/security/EVIDENCE_INTEGRITY.md`, `docs/reference/CONFIGURATION.md`, `docs/research/LIMITATIONS.md`.
