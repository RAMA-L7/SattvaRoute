# Initial documentation audit (Agent A work, performed by coordinator)

Status: Phase 0/1 audit record. No engineering files were changed.

## Repository confirmation

- Repository: `D:\SattvaRoute_publish`, branch `main`, commit `783d7655af36b084fe958c216a54a0b7a58f58d8` (PR #1 squash merge).
- Documentation milestone started with a clean tree; edits in this milestone are all documentation/coordination files.

## Findings

| Finding | Evidence | Resolution |
|---|---|---|
| No single authoritative product definition; entry point mixed product, evidence, and instructions | root `README.md` (pre-overhaul) | Rewrote README as entry point; `docs/product/PRODUCT.md` is authoritative |
| No documentation index / navigation | `docs/` had 100+ files with only `REPORT_INDEX.md` (historical) | Created `docs/DOCUMENTATION_INDEX.md` |
| No authoritative glossary or capability matrix | `docs/reference/` did not exist | Created `docs/reference/GLOSSARY.md`, `CAPABILITIES.md` |
| Outdated test claim: "`tests/` is currently empty; there is no automated suite to claim as passing" | `CONTRIBUTING.md` | Rewrote `CONTRIBUTING.md`: 157 counted `def test_` methods, verified command. An unsupported "166" figure was corrected after independent QA |
| Third-party notice omitted the published Nangate45 / `fakeram45_64x32` package | `THIRD_PARTY_NOTICES.md` (pre-overhaul) | Appended rows + pointer; full inventory in `docs/governance/THIRD_PARTY.md`; LICENSE unchanged |
| Missing root community docs | no `CODE_OF_CONDUCT.md`, `SUPPORT.md` | Created both |
| CITATION title overstated "AI-assisted" | `CITATION.cff` | Updated title/abstract to evidence-driven definition; AI advisory note explicit |
| No Mermaid diagrams | no `.md` with ` ```mermaid ` before overhaul | Created 6 canonical diagrams in `docs/diagrams/` |
| Current-looking legacy notes `docs/architecture.md`, `docs/workflow.md`, `docs/recovery.md` lacked supersession notices | files present | Added header marking historical/superseded with links; original text preserved unchanged |
| Contradiction risk: ASAP7/OpenFinRAM vs Nangate45 control | manifest profiles + historical docs | Established active vs inactive profile terminology in `GLOSSARY.md`, `CONFIG_COLLATERAL.md`, `LIMITATIONS.md`; DRT-0073 left unresolved |
| Contradiction risk: 1000 ns vs 1 ns | `constraint.sdc`, `constraint_1ns.sdc`, `docs/TIMING_AUDIT.md` | Documented as historical executed vs approved correction; no evidence rewritten |
| Contradiction risk: AI-driven recovery | `live_diagnosis.py`, `docs/HELDOUT_RECOVERY.md` | Explicit deterministic classification for recoveries; live AI advisory/unavailable |
| Missing CLI/config reference with verified commands | source exists; no consolidated reference | Created `docs/reference/CLI.md`, `CONFIGURATION.md`, `STATUS_CODES.md`, `ARTIFACTS.md`, `FAILURE_CLASSIFICATIONS.md`, `FAQ.md` |

## Single sources of truth established

- Product definition: `docs/product/PRODUCT.md`
- Terminology: `docs/reference/GLOSSARY.md`
- Capabilities: `docs/reference/CAPABILITIES.md`
- Pinned reproducibility facts/commands: `docs/REPRODUCIBILITY.md`
- Licensing: `LICENSE` + `docs/governance/LICENSING.md` + `docs/governance/THIRD_PARTY.md`
- Historical reports: existing `docs/` files + `docs/REPORT_INDEX.md` (unchanged)

## Non-actionable findings (recorded, not fixed)

- DRT-0073/OpenFinRAM unresolved: preserved, excluded, not reopened.
- Live AI unavailable without credentials: documented, not enabled.
- License change: recommendation only, owner decision; no change.
- Independent external reproduction: not performed; stated as limitation.

## Related

`docs/audit/QA_FINAL.md`, `docs/audit/CLAIM_EVIDENCE.md`, `docs/DOCUMENTATION_INDEX.md`.

## Independent QA (Agent F) follow-ups, appended

- An unsupported "166 passed / 166 tests" figure was found in five new documents and root files. Corrected everywhere to "157 `def test_` methods defined in `tests/*.py` (counted here); prior records report suites passing; not re-executed in this shell".
- `verify_run.py` has no `--json` flag (only in its module docstring). Removed from `docs/reference/CLI.md` and `docs/architecture/VERIFICATION.md`.
- Cross-references pointed to nonexistent `docs/security/APPROVAL_MODEL.md`, `docs/security/AI_RISKS.md`, `docs/security/PATCH_POLICY.md`, `docs/workflow/RECOVERY_FLOW.md`. Repointed to existing `docs/security/SAFETY.md`, `docs/security/INPUT_AND_AI_RISKS.md`, `docs/workflow/WORKFLOW.md`. Markdown link check remains at 0 broken links.
- `benchmark/design/nangate_macro_control/config.mk` has overridable `/mnt/d/...` defaults for `WORK_HOME` and `KLAYOUT_CMD`; "no machine-specific paths" claims were corrected in current docs, and a QA correction note was appended to `docs/REPRODUCIBILITY.md`. The config file was not changed.
- `docs/HELDOUT_RECOVERY.md` contains pre-existing raw control bytes that corrupt a few words. It is a historical evidence record; left unchanged and recorded as an owner-review follow-up in `docs/audit/QA_FINAL.md`.
- "Timing audit" capability was downgraded from VALIDATED to IMPLEMENTED because no unit test references `scripts/timing_audit.py`.
- `docs/security/SAFETY.md` now distinguishes approval-record fields from CLI arguments; threat-model source citations corrected.
