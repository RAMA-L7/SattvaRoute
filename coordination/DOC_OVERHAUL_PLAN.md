# SattvaRoute | Documentation & Product Identity Overhaul (Coordination Plan)

Status: ACTIVE (documentation-only milestone). Repository `D:\SattvaRoute_publish`, branch `main`, commit `783d7655af36b084fe958c216a54a0b7a58f58d8`.
Scope authorization: documentation/product-definition only. **No production source, recovery, diagnosis, runner, approval, verifier, benchmark RTL/config/SDC/LEF/Liberty/collateral change. No new experiments. No ORFS/OpenROAD. No DRT-0073/OpenFinRAM. No LICENSE change. No push/PR/merge. No historical rewrite.**

## Coordinator
Coordinator owns milestone, authoritative scope, shared terminology, ownership, reconciliation, final QA, completion report. Approves shared narrative before dependent docs.

## Shared terminology (authored by coordinator; Agents defer)
Authoritative terminology dictionary: `docs/reference/GLOSSARY.md`. Until created, use terms in `docs/product/TERMINOLOGY.md` draft. Statuses: `PASS/FAIL/BLOCKED/UNKNOWN/INCONCLUSIVE/NOT RUN/NOT EVALUATED`. Capability statuses: `IMPLEMENTED/VALIDATED/EXPERIMENTAL/PARTIALLY IMPLEMENTED/PLANNED/BLOCKED/NOT IMPLEMENTED`. Distinguish **deterministic diagnosis** vs **AI/model diagnosis**; **baseline** vs **failure** vs **recovery attempt/run**; **proposal** vs **approved change**; **verification** vs **engineering validation**.

## File ownership (no two agents edit same doc simultaneously)
- **Coordinator**: `README.md`, `docs/DOCUMENTATION_INDEX.md`, integration, `PROJECT_STATE.md` (append only, not rewrite history), `coordination/*`, final.
- **Agent A**: `docs/audit/*`, inventory/contradiction reports (not edit product docs).
- **Agent B**: `docs/product/PRODUCT.md`, `PROBLEM.md`, `MISSION.md`, `GOALS.md`, `NON_GOALS.md`, `USERS.md`, `USE_CASES.md`, `VALUE.md`, `NAMING.md`, `ROADMAP.md`, `VISION.md`.
- **Agent C**: `docs/architecture/*`, `docs/engineering/*`, `docs/reference/GLOSSARY.md`, failure taxonomy, timing/SDC, reproducibility notes.
- **Agent D**: `docs/security/*`, `docs/governance/SECURITY.md`, `docs/governance/LICENSING.md`, `docs/governance/THIRD_PARTY.md`, `docs/governance/CONTRIBUTING`/`GOVERNANCE`, `SECURITY.md`, `THIRD_PARTY_NOTICES` (append recommendations only; no license change), threat model.
- **Agent E**: `docs/reference/*` navigation, Mermaid files `docs/diagrams/*`, markdown/UX quality.
- **Agent F**: `docs/audit/QA_*`, no edits to product docs; produces findings only.

## Document interfaces
Product narrative authoritative = `docs/product/PRODUCT.md`. Architecture = `docs/architecture/`. Security = `docs/security/`. Terms = `docs/reference/GLOSSARY.md`. Capability matrix = `docs/reference/CAPABILITIES.md`.

## Phases
0 repo+coord audit; 1 evidence audit; 2 narrative+terms; 3 architecture+ownership; 4 parallel authoring; 5 security+license; 6 integration; 7 independent QA; 8 final report. No Git history change.

## Local skills (inspected; none installed)
`D:\agent-skills\skills`, `~/.claude/skills`, `D:\SattvaRoute_publish\.skills`, `D:\SattvaRoute\.skills`. Selected relevant recorded by Agent E + `docs/audit/SKILLS_USED.md`. `graphify` used read-only for codebase mapping context (not required). No motion-forge for docs unless useful; no installs.

## Background agents launched
- Agent A `ses_de796494fffeY2XhbeDJiYn649`
- Agent C `ses_de79615deffeD4u4PKsqYHPHyA`
- Agent D `ses_de7958c4cffeDfrpbZJ2YXSPgy`
- Agent B `ses_de7953573ffey0R40SEJUsc9E2`
- Agent E `ses_de7942364ffeuVZgf7wbRH7TQU`

## Milestone outcome (appended; do not overwrite earlier plan)

- Outcome: documentation-only overhaul completed by coordinator after Agents A-E failed (service overload / free usage limits). No installs.
- Delivered: authoritative product narrative, glossary, capability matrix, documentation index, 6 Mermaid diagrams, architecture/engineering/workflow/security/reproducibility/reference/governance/research docs, root community docs, and audit records in `docs/audit/`.
- README rewritten as entry point; CONTRIBUTING corrected (157 counted offline test methods); CITATION/SECURITY/THIRD_PARTY_NOTICES supplemented; three legacy notes marked superseded with headers only.
- Verification: 249 Markdown files, 0 broken relative links, 6 Mermaid blocks, balanced fences; claim-to-evidence table and QA in `docs/audit/`.
- Scope: no production code, benchmark, SDC, LEF/Liberty, evidence, evaluation, approval, history, LICENSE change; no new experiments, recovery, push, PR, or merge.
- Unresolved: DRT-0073; live AI without credentials; external independent reproduction; license recommendation (owner decision); test suite not re-executed here (Python unavailable in shell).
