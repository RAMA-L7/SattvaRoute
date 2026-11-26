# Failure taxonomy

Status: classes are drawn from implemented diagnosis families and observed evidence. Historical investigations are preserved in `docs/` and not rewritten here.

## Implemented diagnosis families

From `scripts/diagnosis_agent.py`:

| Family | Typical evidence | Notes |
|---|---|---|
| `MISSING_LIB` | `No rule to make target ... .lib`, missing path in resolved `ADDITIONAL_LIBS`/`SC_LIB`/`MACRO_LIB` | Macro or standard-cell Liberty absent |
| `MISSING_LEF` | Missing `.lef` target, resolved LEF variable points to absent file | Includes held-out `ADDITIONAL_LEFS` case |
| `MISSING_TECH_LEF` | Missing technology LEF | Technology/collateral mismatch |
| `MISSING_SC_LIB` / `MISSING_SC_LEF` | Missing standard-cell Liberty/LEF | Platform collateral incomplete |
| `MISSING_CONSTRAINT` | Missing `SDC_FILE` target | Constraint absent or misresolved |
| `MISSING_NETLIST` | Missing netlist / `VERILOG_FILES` / `SYNTH_NETLIST_FILES` target | Input netlist unavailable |
| `UNKNOWN_LIB_CELL` | `not found in library` | Cell/library mismatch |
| `PIN_ACCESS` | `No access point`, DRT codes, LEF/Liberty pin geometry | Macro pin-access investigation |
| `INSUFFICIENT_EVIDENCE` | No bounded rule matches | Correct answer is to abstain, not guess |

## Cross-cutting failure mechanisms

- **Configuration resolution ambiguity** — multiline declarations, `$(shell …)`, multiple library paths, attempt-local overrides. Effective value ≠ declared value.
- **Timing-unit mistakes** — bare numbers interpreted without `report_units`/Liberty `time_unit`; historical 1000 ns vs 1 ns (1000×). See `docs/engineering/SDC_TIMING.md`.
- **Stale/incomplete reports** — empty report, first DRT count, missing-in-both; verified by last count + completion log.
- **Failure propagation** — earliest affected stage invalidates downstream work.
- **Dependency drift** — tool binary, ORFS revision, local patches, collateral hash mismatch.
- **Unsafe correction pressure** — tendency to relax constraints, swap corners, or invent collateral. Bounded by patch validation and approval.
- **Model-related risk** — prompt injection from logs, unsafe generated patches. Advisory-only; see `docs/security/INPUT_AND_AI_RISKS.md`.

## Classification rules

Symptoms are not causes. A diagnosis must bind the mechanism to `evidence_refs` and declare the earliest affected stage. When two mechanisms are plausible and evidence cannot discriminate, the correct status is `INCONCLUSIVE`/`insufficient_evidence`.

## Historical taxonomy material

Earlier detailed investigations (`ENG009`–`ENG015`, `FDE-*`, `WF-*`, `T1-*`) are preserved in `docs/` and indexed in `docs/REPORT_INDEX.md`. They contain historical verdicts (including DRT-0073 / DRT-0305 investigations) and must not be relabeled. This taxonomy describes the implemented classifier, not a replacement for those records.

## Related

`docs/architecture/DIAGNOSIS.md`, `docs/reference/FAILURE_CLASSIFICATIONS.md`, `docs/product/PROBLEM.md`.
