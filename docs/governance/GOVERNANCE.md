# Project governance

Status: project information. Existing coordination history is preserved in `coordination/` and `docs/decisions/`.

## Decision authority

- The **project owner** decides license changes, publication/PR/merge, and scope changes beyond documentation.
- The **coordinator** owns milestone scope, shared terminology, file ownership, reconciliation, and final QA for a workstream.
- Engineers/reviewers produce evidence-backed findings; a claim is accepted only when it maps to source/tests/evidence.
- Historical verdicts are not overridden by new documentation; contradictions are reconciled by linking to authoritative sources and marking superseded docs.

## Coordination artifacts

| Path | Role |
|---|---|
| `AGENTS.md` | Repository operating rules |
| `PROJECT_STATE.md` | Authoritative current snapshot |
| `coordination/TASK_BOARD.md`, `coordination/ACTIVE_WORK.md` | Work ownership / task state |
| `coordination/DOC_OVERHAUL_PLAN.md` | This documentation milestone plan |
| `docs/decisions/DECISIONS.md` | Engineering decision records (D-xxx) |
| `docs/REPORT_INDEX.md` | Historical engineering report index |
| `docs/status/STATUS.md` | Status snapshot |
| `docs/audit/` | Documentation audits and QA |

## Contribution policy

See `CONTRIBUTING.md`. Key rules: feature branches, one logical change, verified commands, no fabricated results, preserve failed experiments, approval status for PnR-affecting changes, report-level verification (`rc=0` insufficient), cites for every engineering claim.

## Release policy

Only the owner publishes or merges. Publication milestone state: `PUBLISHED_REMOTE`; PR #1 `PR_MERGED_VERIFIED` (`https://github.com/RAMA-L7/SattvaRoute/pull/1`). No push/PR/merge is authorized in the documentation-only milestone.

## Support

See `SUPPORT.md` and `SECURITY.md` (private vulnerability reporting).

## Governance constraints

No history rewrite, force-push, deletion of evidence, or relabeling of historical results. No new experiments or production changes in this milestone. License changes require explicit owner approval.

## Related

`docs/governance/DECISIONS.md`, `docs/governance/LICENSING.md`, `docs/governance/RELEASE.md`, `CONTRIBUTING.md`.
