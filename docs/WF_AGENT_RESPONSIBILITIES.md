# T-WORKFLOW-001 — Agent Responsibilities and Orchestration

## Roles (distinct responsibilities)

| Role | Owns | Does NOT do |
|---|---|---|
| Research Engineer | KB retrieval contract, web/documentation/Issue/PR source grading, research-source records | EDA, geometry, ranking decisions |
| EDA Source Engineer | tool/source index, mechanism path classification, source-grounded candidate handoff | production source edits, EDA runs |
| Physical Design Engineer | legality gate G1–G8, physical risk scoring, collateral/all-pin criteria | proposing unproven geometry, execution |
| Validation Engineer | experiment template, controls/metrics, time-budget state machine, tests | declaring PASS from error disappearance |
| Coordinator | execution, integration, ownership, ranking adjudication, conflict resolution, approval gates, authoritative state, publication | concurrent edits with agents |

## Orchestration rules

1. Coordinator declares ownership before any work (`coordination/WORKFLOW_OWNERSHIP.md`).
2. Agents write ONLY their assigned temp reports; read-only on project files.
3. Agents do not read each other's in-progress reports (blind independence).
4. Coordinator integrates findings, resolves conflicts, and is the sole writer of shared files.
5. Independent post-implementation reviewers own only their own review reports.
6. All disagreements are adjudicated in `WF_COORDINATOR_ADJUDICATION.md`.

## Conflict resolution observed

- Agent A ranked LEF OBS `SPACING` / `USEMINSPACING OBS` as top candidates; Agent B proved at source level that those mechanisms affect only abutment/prl spacing, not the confirmed true-overlap Short. **Coordinator adopted B**: stored as `OBS_SPACING_SEMANTICS` refuted family in the remedy KB.
- Agent C concluded no implementable fix is credible; Coordinator's generator inspection confirmed hard-coded full-body OBS. **Adopted**: demonstration stops at the legality gate.

## Independence guarantees

No agent edited another agent's file. No agent ran EDA. No agent modified production artifacts. All final shared-file changes were made by the coordinator and are traceable in the publication commit.
