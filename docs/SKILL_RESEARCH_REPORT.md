# SattvaRoute Skill Discovery and Adoption Research (T-SKILL-002): Final Report

- **Date:** 2026-11-23
- **Type:** research, recommendation and catalog milestone — **no installation performed**
- **Status:** ACCEPTED WITH LIMITATIONS
- **Evidence:** Workstream reports `T2_A_local.md`, `T2_B_gaps.md`, `T2_C_external.md`,
  `T2_D_evaluation.md`, `T2_E_review.md` (temp; commands and outputs preserved there).

## 1. Local skills searched

183 SKILL.md files were inspected across:
- `D:\agent-skills\skills` — 109 skills,
- `C:\Users\91846\.agents\skills` — 52 skills,
- `C:\Users\91846\.config\opencode\skills` — 3 user-level skills,
- `C:\Users\91846\.claude\skills` real directories (`graphify`, `claude-automation-recommender`,
  `motion-graphics`) and 6 agent-desktop bundled skills.

Agent A re-read ~19 SKILL.md files in full and ran a keyword sweep over all 183. Discovery
locations and the earlier 164-name union are recorded in `.skills/DISCOVERY_REPORT.md` and
`skill_sources.json`.

## 2. External discovery

The `find-skills` methodology was used in **search-only** mode: 7 targeted `npx skills find`
queries, all successful (physical design debugging, root cause analysis engineering, scientific
experiment design, EDA OpenROAD Tcl, engineering knowledge management, technical log analysis,
technical code review). No `npx skills add`, `init`, pip, gcloud, gh or other installation command
was executed. 10 candidates were quality-verified against skills.sh pages (install counts, stars,
audit badges) and their **full SKILL.md bodies were retrieved from raw GitHub** at recorded HEAD
SHAs — zero METADATA-ONLY evaluations.

Count snapshot is authoritative from Agent C §4: e.g. `diagnosing-bugs` 964.4K installs / 330.4K
stars, `experimental-design` 1.7K / 58.2K. Intra-report drift (C Q1 963.6K/987.2K) and later
`thananon` 5.0K vs 4.9K are disclosed in `PROJECT_SKILLS.json`. Coverage gap: no credible
OpenROAD/Tcl skill was found; the only true EDA match had 13 installs and was hard-rejected.

## 3. Capability gaps (why skills help at all)

Agent B documented 14 gaps (G1–G14) with file evidence. The four clusters:
1. **Causal-attribution completeness** (FDE-007 ended BLOCKED for lack of `getSrcs()` provenance,
   GDS census at the sliver, spacing/EOL mechanism and all-pin AP evidence) — **not skill-solvable**;
   needs EDA instrumentation and a new decision.
2. **Experiment design validity** — skill-solvable; the controlling gap (no no-op arm, broad carve
   could not discriminate) is exactly what Fisher/DoE discipline addresses.
3. **Report-level PASS adjudication** — only partially skill-solvable; D-007 stays human.
4. **KB ergonomics** — capture/fingerprint/semantic retrieval need code, not skills.

B has two rankings (§0 overall vs §3 skill-solvable); the shortlist uses §3.

## 4. Ranked recommendations

| Rank | Skill | Priority | Status | Adoption mode |
|---|---|---|---|---|
| 1 | `k-dense-ai/scientific-agent-skills@experimental-design` | MUST ADOPT | RECOMMENDED | methodology reference only |
| 2 | `mattpocock/skills@diagnosing-bugs` | MUST ADOPT | RECOMMENDED | methodology reference only |
| 3 | `retrieving-developer-knowledge` (local) | HIGH VALUE | RECOMMENDED | methodology reference only |
| 4 | `thananon/9arm-skills@post-mortem` | HIGH VALUE | RECOMMENDED | methodology reference only |
| 5 | `riekelt/technical-writer@writing-postmortems` | HIGH VALUE | RECOMMENDED | methodology reference only |

Runners-up: `obra/superpowers@receiving-code-review` (HIGH VALUE, redundant with REVIEW_LOG);
`neolabhq@analyse-problem` and `secondsky@code-review` (USEFUL); local `secops-investigate` and
`datalineage-bigquery-asset-impact-analysis` (HIGH VALUE local, compared but not advanced — absent
MCP is not a valid discriminator for text-only adoption). Rejected/quarantined: `hdl-tools@physical-design`
(governance conflict), `graphify`, `anthropic-code-review-framework`, `find-skills` install path.

Full details, sources, versions/SHAs, assigned agents, triggers, dependencies and limitations are in
`.skills/PROJECT_SKILLS.json` and `.skills/PROJECT_SKILLS.md`.

### Why each shortlisted skill is valuable
- **experimental-design** — proper controls, no pseudoreplication, pre-specified bar: prevents the
  exact "inconclusive because the control could not discriminate" ceiling of FDE-005/006U/007.
- **diagnosing-bugs** — falsifiable hypotheses, single-variable instrumentation, red-capable
  feedback: structures reasoning; explicitly *not* a solution to causal-attribution evidence gaps.
- **retrieving-developer-knowledge** — fail-loud tool-result verification, operationalizing
  AGENTS.md rule 9 and D-007.
- **post-mortem / writing-postmortems** — rejected hypotheses, honest validation coverage,
  evidence-only timelines with dated-addendum immutability matching the append-only KB.

## 5. Which agents use them and when

| Agent | Skills | Trigger |
|---|---|---|
| Coordinator | PS-001, PS-005 | pre-run experiment check; final report review |
| Investigation agent | PS-002, PS-003 | new failure characterization; hypothesis ranking |
| Validation agent | PS-001, PS-002 | before controlled experiment / approval gate |
| Review agent | PS-003, PS-006 | review findings, evidence claims |
| Documentation / KB curator | PS-004, PS-005 | FDE completion, handoffs, chronological records |

## 6. Recommended adoption plan

1. **First adoption:** create a **new, separately-approved one-page pre-run experiment design
   checklist** derived from PS-001 (proper control, pseudoreplication, nuisance factors,
   pre-specified acceptance bar). Do **not** edit `AGENTS.md` or any protected/append-only artifact.
2. Then add PS-002 hypothesis/instrumentation guidance and PS-003 fail-loud verification to that
   template.
3. Then PS-004/PS-005 report sections for rejected hypotheses and evidence-only timelines.
4. Any actual skill installation requires a new coordinator approval gate: individual security
   re-audit, inventory and validator update, and an explicit user selection. No auto-integration.

## 7. Security and compatibility

- All shortlisted external skills were audited from full SKILL.md text; GTG/Socket/Snyk results
  recorded. `physical-design` hard-rejected (EDA execution, config self-modification, loop-back).
- `experimental-design` has upstream `uv pip install`, arXiv fetch, scripts and `Write/Bash` tools —
  **excluded**; text only. `post-mortem` JIRA POST, `receiving-code-review` `gh api`, and all
  curl/gcloud credential transports are **excluded**.
- Binding strip-list in `PROJECT_SKILLS.json` adds: no deletions of prototypes/diagnostics/evidence,
  no protected-artifact edits, and **no automatic PASS adjudication — D-007 stays human**.
- Zero-install invariant from D-025 remains intact; no global config changed.

## 8. Files created or updated

**Created:** `.skills/PROJECT_SKILLS.json`, `.skills/PROJECT_SKILLS.md`,
`docs/SKILL_RESEARCH_REPORT.md`, `coordination/LOCKS/T-SKILL-002.lock`, decision D-026.

**Updated:** `coordination/TASK_BOARD.md`, `ACTIVE_WORK.md`, `PROJECT_STATE.md`, `logs/DAILY_LOG.md`,
`logs/AGENT_ACTIVITY.md`, `logs/REVIEW_LOG.md`, `logs/REPORT_LOG.md`, `.skills/INVENTORY.md`,
`scripts/publish_skill.sh` allowlist, session handoff.

## 9. Unresolved issues / limitations

- No skills are installed or active; agents report `NO VALIDATED SKILL AVAILABLE` until a new gate.
- Causal-attribution gaps need EDA instrumentation, not skills; FDE-007 remains BLOCKED.
- Audit depth = SKILL.md text; referenced scripts and repository internals were not fully audited.
- One source-reputation caution (`riekelt`: 41 stars, Snyk WARN) and one low-adoption EDA skill rejected.
- Zero-install is a deliberate invariant, not a failed installation.

## 10. Clear recommendation

**Adopt `k-dense-ai/scientific-agent-skills@experimental-design` first** — as a methodology-only,
separately-approved pre-run experiment design checklist — because experiment-design validity is the
highest-value skill-solvable cause of SattvaRoute's repeated inconclusive/blocked FDE outcomes.
Follow with `mattpocock/skills@diagnosing-bugs`, then the local fail-loud evidence rule and the two
post-mortem writing skills. Do not install any skill as part of this milestone.
