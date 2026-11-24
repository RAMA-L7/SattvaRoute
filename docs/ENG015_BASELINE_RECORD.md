# T-ENGINEERING-015 — Baseline and Integrity Record

> Recorded at research start. Read-only observations; no artifact changed.

## Publication state
- `D:\SattvaRoute_publish`: `main` at `52380bb20cd8eb8dbaa3aace7f8b9c16e2eea68d`, clean, equals `origin/main`.
- Live tree `D:\SattvaRoute`: branch `master` with long-standing uncommitted engineering records; preserved as-is.

## Integrity at research start
- KB verify: PASS, 19 records / 19-link chain.
- `verify-immutable`: PASS, 0 changed (authoritative live tree).
- `.skills/validate_skills.py`: PASS=13 FAIL=0.
- R2 checklist hash `6900ebc8b17821f7b1bb30f29224d0eb120042fd5e392dbbf42046877ba4cb9d` (DRAFT/INACTIVE).

## Protected / baseline hashes (recorded, unchanged)
| Artifact | SHA-256 |
|---|---|
| `docs/ENG014_FINAL_REPORT.md` | `85db8cf120e3092191a5bb19ba52d9d66af87b454c37bc00c8d3edc0e55f0eb2` |
| `docs/ENG013_BLOCKER_ATTRIBUTION.md` | `162c7f10478ed8556675ce80f931ad9878643253779b8bb9830d1365c43e0480` |
| `docs/EXPERIMENT_DESIGN_CHECKLIST.md` | `6900ebc8b17821f7b1bb30f29224d0eb120042fd5e392dbbf42046877ba4cb9d` |
| `benchmark/design/sattva_sram/macro/sram_x4x4x1.lef` | `f1c18877c27152bc81dce3bfa76308f29c9faa54047de4ac5a3f7d160b4bba31` |
| `benchmark/design/sattva_sram/macro/sram_x4x4x1.gds` | `12c56777a060270215ad7c43a881230febc9f3dc272bf9a436da60efd510d651` |
| Production source ODB (`4_cts.odb`) | `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` |
| Broad-carve diagnostic ODB | `616e39f8d9be5cae2452042906e3d187161c3938c2f040c88d3d646f57d457e0` |
| ENG013 instrumented binary | `db876fbf030e3dc4b84e07891e1e3932d476801f8ed30cbc5e562b5f7441c292` |
| ENG013 instrumented source | `797b282ce89f494b36dc44b3ae67c709c85e53054a03a6e894220381af4c3403` |

## Ownership (Phase 1)
See `coordination/ENG015_OWNERSHIP.md`. Agents own only their individual temp reports; coordinator owns all shared files. No concurrent edits.

## Phase boundary
Research is read-only. No Phase 3 execution may occur until a research gate decision is published with candidate, mechanism, evidence, predicted outcome, risks, and preregistered plan. Production merge/publish/deploy remains unauthorized.
