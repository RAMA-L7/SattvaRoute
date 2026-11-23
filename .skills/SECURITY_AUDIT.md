# Skill Security and Integrity Audit — T-SKILL-001

Source: Workstream D report (`SKILL_D_security.md`, temp) plus coordinator verification. All findings
are based on file contents, not descriptions. No project file was modified by the audit.

## 1. Trust boundaries for any future installed skill

1. **Allowed paths:** one dedicated sandbox. Deny by default `benchmark/`, `runs/`, `experiments/`,
   `tools/`, `configs/`, `state/approval_policy.json` and `knowledge/` (append-only; only the
   sanctioned KB process may append).
2. **Read-only defaults:** skills read permitted files; writes confined to the sandbox. Never edit
   approval policy, scripts, CI, KB records or EDA flow files.
3. **No EDA execution:** never invoke OpenROAD, DRC/LVS/timing, `scripts/run_baseline_orfs.sh` or
   any production EDA tool from a skill.
4. **No approval bypass:** no auto-merge, no 0-human tier, no self-approval, no "no confirmation
   needed" execution, no reuse of one-time consent. All gating stays in `sattva_approval.py` and
   `state/approval_policy.json`.
5. **No network without explicit human approval:** block npx/pip installs, curl/requests,
   gcloud/gsutil/gh/kubectl, credential retrieval and external skill installation. Suggested
   commands are reviewed and run manually by an authorized human outside the skill.
6. **No hidden behavior:** reject unreviewed markup-as-instruction, encoded payloads and binaries;
   only vetted SKILL.md text is active.

## 2. Candidate findings

| Candidate | Risk | Finding | Verdict |
|---|---|---|---|
| `anthropic-code-review-framework` | MEDIUM | Prose only, no payload; but "Low: 0 humans (auto-merge on green)" and "low-risk auto-merge" bypass approval; encourages EDA execution and unbounded nightly agents; self-calibrating risk policy | **NOT INSTALLED** — governance conflict + duplicate |
| `claude-95percent-learning-system` | LOW | `<co>…: 21:[0]` markup verified inert (0 zero-width/bidi/control chars); no scripts/network/credentials | NOT INSTALLED — not relevant, unregistered |
| `agent-platform-eval-flywheel` read-only scripts | LOW | stdlib JSON/argparse; some `-o` writes need path control | NOT INSTALLED — not relevant |
| `agent-platform-eval-flywheel` endpoint/maas/deploy | HIGH | `gcloud auth print-access-token` + `requests.post` bearer token to agent-supplied URL (exfil vector); gsutil; unbounded inference; pip installs; "approve once forever" | **QUARANTINE** |
| `find-skills` | MEDIUM-HIGH | `npx skills add <pkg> -g -y` installs unreviewed third-party code globally and skips confirmation; network + npm fetch | **QUARANTINE** (still used as discovery method here) |
| `upstream-pr-contribution` | MEDIUM | Strong guardrails but executes git/gh, forks and PR creation; external writes and credential context | NOT INSTALLED — text guidance only if ever needed |
| `agent-desktop` | MEDIUM-HIGH | Can read any screen content and click approval dialogs; screenshots unredacted | NOT INSTALLED — headless project |
| `graphify` | HIGH (operational) | GitHub clone, uv/pip install, Neo4j/FalkorDB push, watch mode, `graphify-out/` writes; duplicates KB | **QUARANTINE / NOT INSTALLED** |
| `agent-platform-skill-registry` | HIGH | ADC token + POST/GET/DELETE/PATCH to remote skill endpoint; can delete remote skills | **QUARANTINE** |
| `agent-platform-deploy` config script | MEDIUM-HIGH | sets global gcloud config, defaults to `prod` | **QUARANTINE** |
| `dbt-sf-to-bq-translator` | HIGH | `shutil.rmtree`/`os.remove` relative to cwd + subprocess + GCS transfer | **QUARANTINE** |
| `google-cloud-filestore-auditing` | MEDIUM-HIGH | despite "audit" name, emits `gcloud filestore backups create` remediations | **QUARANTINE** |

No prompt-injection payloads, binary blobs or obfuscated content were found in the named primary
candidates. The only base64 use found (skill-registry zip transport) is legitimate.

## 3. Residual risks

- The wider catalog contains ~40 executable files; only the highest-capability ones were audited in
  depth. Any future skill must be audited individually before approval.
- `find-skills` was used for discovery in this task despite being quarantined for installation. Its
  install commands were **never executed**; only local filesystem/MCP enumeration was used.
- Broken junctions in `.claude`/`.roo`/`.continue` are a hygiene issue but do not affect OpenCode
  discovery because the skills exist in the `D:` tree.

## 4. Protected-artifact status during audit

`verify-immutable` was executed and returned PASS 9/9 (production LEF `f1c18877…`, GDS `12c56777…`,
Liberty, config, SDC, approval policy, approval validator, runner, AGENTS.md). KB `verify` returned
PASS with 18 records and an 18-link append chain. No skill touched these artifacts.
