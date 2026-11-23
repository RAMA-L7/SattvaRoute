# SattvaRoute Project Skill Catalog

- **Task:** T-SKILL-002 · **Selection date:** 2026-11-23
- **Authoritative machine-readable record:** `PROJECT_SKILLS.json`
- **Critical status statement:** **zero skills installed, zero active, zero validated.** All entries
  below are DISCOVERED, EVALUATED, RECOMMENDED (methodology reference only) or REJECTED. A
  RECOMMENDED priority is **not** installation authorization; every installation requires a new
  coordinator approval gate. Preserve the D-025 zero-install invariant.

## 1. What skills does SattvaRoute use, and why?

Currently **none**. Agents must report `NO VALIDATED SKILL AVAILABLE` at use time. The entries below
are a vetted shortlist of *methodology references* extracted from external/local skills whose text
improves SattvaRoute's reasoning quality. Their scripts, network calls and file writes are excluded.

## 2. Recommended (methodology reference only)

### PS-001 — k-dense-ai/scientific-agent-skills@experimental-design — MUST ADOPT
- **What it does:** Fisher randomization/replication/blocking, reproducible DoE layouts; rejects
  pseudoreplication, demands a pre-specified analysis.
- **Why:** addresses G5/G6/G3 — the FDE-005/006U/007 "inconclusive because no proper control or
  no-op arm" ceiling (FDE-007:24,31-33). This is the highest-value skill-solvable gap (B §3).
- **Where / when:** coordinator and validation agent, before any controlled experiment or remedy
  approval gate; one-page pre-run checklist.
- **Value:** better experiment validity and evidence completeness before a run is authorized.
- **Source/version:** skills.sh page; v1.5 (2026-09-30, MIT), HEAD `c21d13b3cc28`.
- **Status:** RECOMMENDED — not installed, not active. Upstream `uv pip install`, arXiv fetch,
  scripts and Write/Bash directives are excluded.
- **Verbatim vs inferred:** Fisher principles and "Pre-specify the analysis" are verbatim; the
  mapping to SattvaRoute FDE gaps is INFERRED.

### PS-002 — mattpocock/skills@diagnosing-bugs — MUST ADOPT
- **What it does:** red-capable feedback loop, minimize, 3–5 falsifiable hypotheses, one-variable
  instrumentation, regression-first fix, cleanup.
- **Why:** improves B5/B3 reasoning (G7/G8/G3) — falsifiable hypotheses and single-variable
  instrumentation mirror what FDE-004..006 had to invent ad hoc.
- **Where / when:** investigation agent and validation agent; new failure characterization and
  hypothesis ranking.
- **Important correction:** this skill does **not** close the causal-attribution gap B §0 #1.
  `getSrcs()` provenance, GDS census and all-pin AP evidence require EDA instrumentation and a new
  decision (B §2:132-144; FDE-007:33).
- **Source/version:** skills.sh page; HEAD `abeeaf95660b`.
- **Status:** RECOMMENDED — not installed, not active. Referenced scripts and curl/dev-server
  suggestions excluded; secret-redaction rule retained.

### PS-003 — retrieving-developer-knowledge (local) — HIGH VALUE
- **What it does:** fail-loud lookup verification — an error/empty/401/403 payload is a FAILED
  lookup even when the tool reported no error; recalled documentation presented as retrieved is
  the worst outcome.
- **Why:** operationalizes AGENTS.md rule 9 and D-007; directly improves evidence integrity.
- **Where / when:** all agents, whenever a claim rests on tool output. Advanced after independent
  review noted it was omitted by earlier evaluation; absent Google-docs transport is irrelevant for
  text-only adoption.
- **Source/version:** `C:/Users/91846/.agents/skills/...`, SHA-256 `df710e2b4cba4d…`.
- **Status:** RECOMMENDED — not installed. curl/gcloud credential transport forbidden.

### PS-004 — thananon/9arm-skills@post-mortem — HIGH VALUE
- **What it does:** validated-fix postmortem with rejected-hypothesis block and honest validation
  coverage.
- **Why:** improves B4+B3 (G12/G7) final FDE reports.
- **Where / when:** documentation agent; FDE completion.
- **Source/version:** skills.sh page; HEAD `a1fc303b274e`; snapshot 4.9K installs.
- **Status:** RECOMMENDED — not installed. JIRA POST stripped. Its "refuse without 4 inputs" rule
  must not suppress INCONCLUSIVE/BLOCKED FDE reports.

### PS-005 — riekelt/technical-writer@writing-postmortems — HIGH VALUE
- **What it does:** evidence-only timeline, immutability by dated addendum.
- **Why:** maps to the append-only KB and dated logs (KNOWLEDGE_BASE.md:34-35,204-206).
- **Where / when:** documentation agent and KB curator; chronological records.
- **Source/version:** skills.sh page; HEAD `85e53729dd95`; 27.3K installs but 41 stars (flagged).
- **Status:** RECOMMENDED — not installed. Reputation caution; no install authorized.

### PS-006 — obra/superpowers@receiving-code-review — HIGH VALUE (runner-up)
- **What it does:** verify review feedback with technical rigor before agreement.
- **Why / status:** improves B5/G7/G8 but largely redundant with `logs/REVIEW_LOG.md`.
  `gh api` and "human partner" authority stripped; RECOMMENDED, not installed.

## 3. Evaluated but not advanced

| ID | Skill | Priority | Reason |
|---|---|---|---|
| PS-007 | secops-investigate (local) | HIGH VALUE (local) | timeline/scope/untrusted-telemetry methods; at least as good as PS-002 for report structure, compared but not advanced to avoid bloat. SecOps MCP absent; no MCP calls. |
| PS-008 | datalineage-bigquery-asset-impact-analysis (local) | HIGH VALUE (local) | depth/staleness blast-radius reasoning beyond KB links; needs absent Data Lineage MCP/bq; compared only. |
| PS-009 | neolabhq@analyse-problem | USEFUL | A3 structure; redundant with FDE templates. |
| PS-010 | secondsky@code-review | USEFUL (redundant) | 558 installs; redundant with PS-006. |
| PS-011 | mattpocock@codebase-design | OPTIONAL | clean but weak fit to process gaps; project in frozen state. |
| PS-012 | neolabhq@why | OPTIONAL | subsumed by PS-009/PS-002. |

## 4. Rejected / quarantined

| ID | Skill | Reason |
|---|---|---|
| PS-013 | hdl-tools/digital-chip-design-agents@physical-design | Only true EDA match (13 installs) but spawns EDA orchestrator, self-modifies config/constraints, loops back — violates no-EDA, protected paths, approval gates. Four evidence sentences only. |
| PS-014 | graphify | Inference labeling/path queries are useful conceptually, but execution needs uv/pip, GitHub clone, Neo4j/FalkorDB push, watch mode, Gemini key. Prior quarantine binding. Text-only rules (EXTRACTED/INFERRED/AMBIGUOUS, never invent an edge). |
| PS-015 | anthropic-code-review-framework | 0-human auto-merge, self-calibrating risk policy, assumed CI/branch protection conflict with approval gates; duplicates REVIEW_LOG. Text-only file:line rule and incident-to-eval loop only. |

`find-skills` remains the discovery method for this milestone but is QUARANTINED for installation
(`npx skills add -g -y` installs unreviewed third-party code globally). No install command was run.

## 5. Binding strip-list (from PROJECT_SKILLS.json)

- No installation or global config change without a new coordinator approval gate.
- No skill executes EDA/OpenROAD/DRC/LVS/timing or modifies production/design/ORFS inputs.
- No edits to `AGENTS.md`, `REVIEW_LOG.md`, `knowledge/` or any protected artifact from skill guidance.
- No deletion of prototypes, diagnostics, logs or evidence (AGENTS.md:5,59).
- No credential retrieval, `gh api`, JIRA POST, curl/gcloud transport, pip/uv installs or network calls.
- **No automatic PASS adjudication: D-007 report-level human review stays binding.**
- No auto-merge, 0-human tier, self-approval or loop-back remediation without approval.
- No skill instruction outranks `AGENTS.md`, `PROJECT_STATE.md` or approval gates.
- Agents report skill name/version and label skill-derived recommendations separately; otherwise
  state `NO VALIDATED SKILL AVAILABLE`.

## 6. First adoption recommendation

Adopt **PS-001 experimental-design first** as a **new, separately-approved one-page pre-run design
checklist** (new template file), not as an edit to `AGENTS.md` or any protected artifact. Then
PS-002, then PS-003..PS-005. No skill installation is part of this recommendation.
