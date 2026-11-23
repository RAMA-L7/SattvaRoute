# Skill Discovery Report — T-SKILL-001

- **Date:** 2026-11-23
- **Scope:** all skill sources available to the local agent environment; no installation attempted.
- **Method:** filesystem enumeration, config inspection, MCP queries, content sampling.
- **Evidence:** full command/output ledger in Workstream A report (`SKILL_A_discovery.md`, temp).

## 1. Discovery scope and environment

| Source | Path | Result |
|---|---|---|
| OpenCode configured root | `D:/agent-skills/skills` (opencode.jsonc lines 35–37) | 110 dirs; 109 with SKILL.md; 17-dir nested container |
| Second first-party tree | `C:/Users/91846/.agents/skills` | 52 with SKILL.md (+1 new `motionsites-web-builder` appeared mid-session) |
| User-level OpenCode skills | `C:/Users/91846/.config/opencode/skills` | 3: motion-graphics, upstream-pr-contribution, youtube-comment |
| Claude Code aliases | `C:/Users/91846/.claude/skills` | 171 entries; 168 junctions (95 broken, 73 resolving); 3 real dirs |
| Roo / Continue mirrors | `.roo/skills`, `.continue/skills` | 147 entries each; same broken-junction pattern |
| MCP skill tools | `agent-desktop desktop_skills_list` | 6 bundled skills (desktop, macos, windows, linux, ffi, jev) |
| MCP resources | `opencode.list_mcp_resources` | `{resources:[], templates:[]}` |
| Other MCP servers | openroad-mcp, playwright, shadcn, firecrawl, context7 | tools, not skills |
| Network registry | `https://skills.sh/` HEAD | HTTP 308 → `https://www.skills.sh/`; not used for installation |
| Tooling | node v26.7.0 / npx 12.1.0 | present; no install executed |

**Unique skill names with SKILL.md across first-party sources: 164.** Duplicates: D∩A = 0;
D∩U = 2; nested `skills/` container adds 17 duplicate names. The 95 broken `.claude` junctions point
to absent `.agents` targets, but the affected skills also exist in the D: tree, so no skill becomes
unloadable because of them.

## 2. Discovery commands (representative, all read-only)

- `Get-ChildItem 'D:\agent-skills\skills' -Directory -Force` → 110 entries.
- `Get-ChildItem 'C:\Users\91846\.agents\skills' -Directory` → 52 (+1 new).
- `Select-String -Path opencode.jsonc -Pattern 'skill'` → lines 35–37 single configured root.
- `agent-desktop skills list` (MCP) → 6 bundled skills.
- `opencode.list_mcp_resources({})` → empty.
- `curl -I --max-time 15 https://skills.sh/` → 308 redirect.
- First-party grep for `@skill|SKILL.md|.agents/skills|.claude/skills|graphify|openroad-mcp`
  (excluding `experiments/`, `.git`) → **zero matches**: no skill usage in SattvaRoute.

## 3. Skills already installed in the project

**None.** `D:\SattvaRoute\.skills` did not exist before this task. The only SKILL.md files inside the
repository are in a vendored OpenROAD source snapshot under
`experiments/FDE-006/.../source/OpenROAD/.agents/skills/{add-test,fix-bug,review-pr,triage-issue}` —
upstream content, explicitly out of scope and read-only.

## 4. Relevant candidates

By capability area (candidate list only; evaluation is in `EVALUATION_SUMMARY.md`):

- Engineering investigation: `secops-investigate`, `secops-hunt`, `secops-triage`, `retrieving-developer-knowledge`.
- OpenROAD/ORFS: **no dedicated skill exists**; relevant asset is the `openroad-mcp` MCP server + README.
- Knowledge management: `graphify`, `datalineage-summary`, `claude-95percent-learning-system`.
- Evidence integrity: `workload-manager-basics`, `secops-cases`, `google-cloud-scc-query`.
- Orchestration: `desktop-browser-orchestrator`, `agent-desktop`, `agent-platform-*`.
- Review / QA: `anthropic-code-review-framework`, `upstream-pr-contribution`.
- Project operations: `find-skills`, `finding-google-skills`, `gcloud`, `context7-mcp`.

Not relevant: adobe-*, google-mobile-ads-*, motion-graphics, scroll-craft, hallmark, magic-ui,
jack-roberts-youtube-framework, youtube-comment, motionsites-web-builder.

## 5. Duplicates, rejected and blocked

- **Duplicates:** nested `skills/` 17 names; D∩U = 2; `graphify` duplicates the SattvaRoute KB;
  `anthropic-code-review-framework` duplicates existing review gates and `logs/REVIEW_LOG.md`.
- **Rejected:** all cloud/GKE/SecOps/BigQuery/adobe/design skills as not relevant to a headless ASAP7/ORFS flow.
- **Blocked / quarantined:** `find-skills` (global-install authority), eval-flywheel deployment subset,
  skill-registry, deploy-config, dbt-translator, filestore-auditing, graphify.
- **Note:** Workstream C reported `graphify` as a broken junction; Workstream A and direct inspection
  found a real `SKILL.md` at `C:\Users\91846\.claude\skills\graphify\SKILL.md`. The path detail in C is
  incorrect; the *disposition* (not installed) is unchanged because graphify is a KB duplicate with
  network/install/external-DB behavior.

## 6. Security observations

No prompt-injection payloads, binaries or obfuscated content were found in the primary candidates.
High-capability script-bearing skills in the wider catalog can fetch tokens, push to external
databases, mutate global CLI config, or delete files relative to cwd — see `SECURITY_AUDIT.md`.
`find-skills` itself contains an unreviewed global-install command (`npx skills add -g -y`) and is
quarantined despite being used as this task's discovery method.

## 7. Installation plan (decided)

**Install nothing.** Workstream B verified that all six capability areas are already implemented in
project code/process; Workstream C found no REQUIRED skill; Workstream D quarantined the only
plausible discovery tool. Document the empty install honestly in `INVENTORY.md` and
`INSTALLATION_REPORT.md`, add agent usage rules, validate the empty-install invariant, and publish.
