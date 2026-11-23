# SattvaRoute Project Skill Inventory

- **Task:** T-SKILL-001
- **Last verified:** 2026-11-23
- **Authority:** this is the authoritative inventory of skills used **specifically by SattvaRoute**.
- **Coordinator decision:** **zero skills approved, zero installed, zero active** (see `INSTALLATION_REPORT.md`).

The categories below are deliberately kept distinct and must never be treated as interchangeable.

| Category | Count | Evidence |
|---|---|---|
| Discovered (unique names with SKILL.md, all first-party sources) | 164 | `DISCOVERY_REPORT.md`, `skill_sources.json` |
| Evaluated in depth | 11 | `SKILL_C_evaluation.md` (temp report), `EVALUATION_SUMMARY.md` |
| Approved for installation | 0 | coordinator decision; all workflows already implemented (`SKILL_B_requirements.md`) |
| Installed project-locally | 0 | `INSTALLATION_REPORT.md`; `.skills/` contains no skill directories |
| Tested as installed skills | 0 | `validate_skills.py` validates the empty-install invariant instead |
| Actively used by SattvaRoute agents | 0 | no first-party skill usage evidence in the repository |
| Rejected (DUPLICATE / UNSAFE / governance conflict) | 2 primary | `anthropic-code-review-framework`, `graphify` |
| Quarantined (do not install) | 7 | `SECURITY_AUDIT.md` |

## Installed skills

**None.** No project skill directories were created. The proposed `engineering-investigation/`,
`openroad-orfs/`, `knowledge-base/`, `evidence-integrity/`, `experiment-design/`,
`multi-agent-orchestration/`, `engineering-review/` and `project-operations/` folders were
deliberately **not** created: no validated skill exists for them, and empty placeholders are
forbidden by the mission.

## Skills used during this task (not installed)

| Skill | Source | Version/hash | Use | Installation status |
|---|---|---|---|---|
| `find-skills` | `D:\agent-skills\skills\find-skills\SKILL.md` | SHA-256 `c1d9628984991d7ed59ab3a7bf6a4dad3d731ef68c71f409f64a0ca258e8028e` | discovery method for T-SKILL-001 only | **QUARANTINED** — its `npx skills add -g -y` path installs unreviewed third-party code globally; no installation performed |

No other skill materially influenced project work. `openroad-mcp` is an MCP server (not a skill)
already connected in the environment and is documented in `README.md` as an available read-only
introspection tool; it was not installed or changed by this task.

## Evaluated but not installed

| Skill | Source | Assessment | Disposition |
|---|---|---|---|
| `anthropic-code-review-framework` | `D:\agent-skills\skills\...` SHA-256 `312211c321e2fecf0073f56b7f82178c7e13c3a20d0e6d83be4d235d401cd898` | DUPLICATE of FDE review gates + `logs/REVIEW_LOG.md`; "0 humans / auto-merge on green" bypasses approval; requires non-existent CI/branch protection; no YAML frontmatter (unregistered) | NOT INSTALLED — DUPLICATE / UNSAFE |
| `graphify` | `C:\Users\91846\.claude\skills\graphify\SKILL.md` | DUPLICATE of `scripts/sattva_kb.py` + `knowledge/`; GitHub cloning, `uv`/`pip` installs, Neo4j/FalkorDB push, watch mode | NOT INSTALLED — DUPLICATE / HIGH operational risk |
| `claude-95percent-learning-system` | SHA-256 `b4f1d3613aadf63317ca407d8b26ccb351f2eb069faa0b8682b5c5219aed3e7e` | unrelated tutorial; inert `<co>` markup; no frontmatter | NOT INSTALLED — NOT RELEVANT |
| `agent-platform-eval-flywheel` | SHA-256 `877715295b30f64550affc4c912ffcb54cb312540d1479d3b62840b8734e6964` | GCP SDK/credentials/billed inference; deployment subset HIGH risk | NOT INSTALLED / QUARANTINED |
| `upstream-pr-contribution` | SHA-256 `20d3edc010a19b0f7158db760588d50a3e710524d4f9ec23e2977ca3aa1d7291` | PR workflow not used by this project (direct reviewed push); git/gh credentials | NOT INSTALLED — OPTIONAL only |
| `annotated-illustration` | SHA-256 `815e11d81b5ad279b17c063a621193a740207d9955763bcd5518feec798a361b` | generated visuals could be mistaken for measured evidence | NOT INSTALLED — NOT RELEVANT |
| `agent-desktop` | SHA-256 `9837b299a48080db37865c6ac6edbfacaf3d4ccbf0f86d4fbd85477619a9ab0d` | headless project; GUI evidence inadmissible here | NOT INSTALLED — NOT RELEVANT |

## Quarantined (must not be installed without a new security review)

`find-skills` (global install authority), `agent-platform-eval-flywheel` deployment subset
(`endpoint_evaluation.py`, `maas_evaluation.py`, `references/deployment.md`),
`agent-platform-skill-registry` (remote skill delete/patch), `agent-platform-deploy` config script,
`dbt-sf-to-bq-translator` (cwd-relative deletion), `google-cloud-filestore-auditing` (cloud-write
remediations), `graphify` (network/install/external DB push).

## Validation

`python3 .skills/validate_skills.py` — offline, stdlib-only. Result at this checkpoint: see
`INSTALLATION_REPORT.md` and `logs/REVIEW_LOG.md` (R-013).
