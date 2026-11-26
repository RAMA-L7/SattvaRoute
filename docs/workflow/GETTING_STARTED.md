# Getting started

Status: commands verified against `scripts/pnr_cli.py`, `manifest.py`, `verify_run.py`, `timing_audit.py`, and `docs/REPRODUCIBILITY.md`.

## Prerequisites

- Python ≥ 3.10, GNU Make, Bash.
- An external ORFS checkout at pinned revision `25b6429c1644a8682852646bebf19ff164402c76` with the two declared local patches applied (paths, reasons and SHA-256 in `config/sattva_manifest.json`; the runner-generated `evidence/mirror.patch` is not published).
- Pinned OpenROAD and Yosys binaries (hashes in `config/sattva_manifest.json`).
- No network credentials required for offline diagnosis/tests. A model provider is optional and advisory.

Nothing is vendored: ORFS, PDKs, tool binaries, and platform libraries are external. See `docs/governance/THIRD_PARTY.md`.

## Environment

| Variable | Meaning |
|---|---|
| `SATTVA_ROOT` | Project checkout root |
| `SATTVA_MIRROR` | ORFS checkout (default `$SATTVA_ROOT/tools/OpenROAD-flow-scripts`) |
| `SATTVA_DESIGN` | Design directory (control: `benchmark/design/nangate_macro_control`) |
| `SATTVA_DESIGN_PROFILE` | Active manifest profile (`nangate_macro_control`) |
| `OPENROAD_EXE` / `YOSYS_EXE` | Tool binary overrides |
| `SATTVA_MODEL_URL` (optional) | Model provider for advisory live diagnosis; unset → no live AI |

## Acquire pinned dependencies (deterministic)

```
git clone https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts
git -C OpenROAD-flow-scripts checkout 25b6429c1644a8682852646bebf19ff164402c76
# apply the two local patches declared in config/sattva_manifest.json
# build openroad + yosys to match pinned sha256 in config/sattva_manifest.json
export SATTVA_MIRROR=<checkout>
```

## Verify setup (no flow run)

```
python3 scripts/manifest.py --check --profile nangate_macro_control --mirror "$SATTVA_MIRROR"
python3 scripts/pnr_cli.py status
```

`status` reports manifest digest, control benchmark path, and the approval-gate reminder. Note: `pnr_cli.py status` prints top-level `PASS` and a nested `manifest` result; it does not propagate `manifest.py --check` failures to its own exit code. Use `python3 scripts/manifest.py --check --profile nangate_macro_control --mirror <orfs>` as the authoritative preflight gate (it returns non-zero on mismatch).

## Offline tests (no credentials, no flow)

```
python3 -m unittest discover -s tests -p 'test_*.py'
```

The suite defines 157 test methods across `tests/test_*.py` (counted in this milestone), covering approval integrity, diagnosis, manifest, recovery CLI, verification, KB, remedy engine, and evaluation v2. Prior records report the suites passing; no re-execution occurred here (no Python interpreter in this shell).

## First baseline run

```
SATTVA_ROOT=<checkout> SATTVA_MIRROR=<orfs> \
  python3 scripts/pnr_cli.py baseline --tag control_first
```

Then verify independently:

```
python3 scripts/verify_run.py --run <run-dir> --audit <audit.json>
```

`baseline` prints `engineering_verdict: NOT EVALUATED - inspect reports`; the verdict comes from `verify_run.py`, not from its return code.

## Next steps

Follow `docs/workflow/WORKFLOW.md` for diagnosis → proposal → approval → recovery → verification. Read `docs/security/SAFETY.md` before applying any change. See `docs/workflow/TROUBLESHOOTING.md` if preflight or verification fails.

## Related

`docs/REPRODUCIBILITY.md`, `docs/reference/CLI.md`, `docs/reference/CONFIGURATION.md`.
