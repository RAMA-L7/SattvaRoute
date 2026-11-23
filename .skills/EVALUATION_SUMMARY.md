# Skill Evaluation Summary — T-SKILL-001

Eleven candidates were evaluated from actual SKILL.md/script contents (Workstream C report
`SKILL_C_evaluation.md`, temp). Scores are 0–10 relevance to SattvaRoute's actual workflow.

| Rank | Candidate | Score | Recommendation | Basis |
|---|---|---|---|---|
| 1 | `openroad-mcp` (MCP server, not a skill) | 7 | RECOMMENDED read-only tool | already connected; ODB/Tcl introspection; no install needed |
| 2 | `upstream-pr-contribution` | 4 | OPTIONAL | project publishes via reviewed direct push, not PRs; git/gh credentials |
| 3 | `find-skills` | 3 | OPTIONAL search only / QUARANTINE install | used here; `npx skills add -g -y` is an unreviewed global install |
| 4 | `anthropic-code-review-framework` | 4 | UNSAFE / DUPLICATE | 0-human auto-merge; CI/branch-protection changes; duplicates `REVIEW_LOG.md`; no frontmatter |
| 5 | `agent-platform-eval-flywheel` | 3 | NOT RELEVANT / QUARANTINE subset | GCP credentials, billed inference; deployment scripts HIGH risk |
| 6 | `retrieving-developer-knowledge` | 3 | NOT RELEVANT | external docs cannot establish local ODB/log/GDS facts |
| 7 | `annotated-illustration` | 2 | NOT RELEVANT | generated visuals risk being mistaken for measured evidence |
| 8 | `agent-desktop` | 2 | NOT RELEVANT | headless project; GUI snapshots are not admissible evidence |
| 9 | `desktop-browser-orchestrator` | 2 | NOT RELEVANT | no browser/desktop step in ORFS pipeline |
| 10 | `claude-95percent-learning-system` | 1 | NOT RELEVANT | tutorial for another product's UI; inert markup; no frontmatter |
| 11 | `graphify` | 0 | NOT INSTALLED — DUPLICATE / HIGH RISK | duplicates `sattva_kb.py`; clones repos, installs deps, pushes to Neo4j/FalkorDB |

A full 110-directory scan found no other skill genuinely covering investigation, evidence,
knowledge, orchestration or physical design. Near-misses (GKE, SecOps, BigQuery) are domain-specific.

## Coordinator decision

**No skill is REQUIRED. No skill is installed.** Workstream B established that all capability areas
are already implemented by deterministic project code (`scripts/sattva_approval.py`,
`scripts/run_baseline_orfs.sh`, `scripts/sattva_kb.py`, `scripts/publish_kb.sh`) and process
(`AGENTS.md`, `coordination/`, `logs/`, FDE reports, D-007). Installing a skill would duplicate or,
in the case of the review framework, directly conflict with approval controls.

`openroad-mcp` remains available as an **existing MCP tool** for read-only introspection; it is not a
project skill and was not modified. Any future use must remain read-only (no `write_db`, no direct
PnR control, no production paths, no patch application outside the approval gate).
