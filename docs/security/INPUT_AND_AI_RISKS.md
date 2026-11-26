# Input handling, AI risks, and credential hygiene

Status: documentation-level audit; no controls added.

## Input handling risks

| Risk | Observed behavior | Remaining risk |
|---|---|---|
| Malformed logs | `verify_run.py` and `diagnosis_agent.py` read with `errors="replace"` and bounded regexes | Not a hardened parser; fuzzing not performed |
| Malformed `.lib`/`.lef`/SDC/netlist | Treated as untrusted content; collateral pinned by hash | Parsing delegated to external tools; no schema validation |
| Ambiguous Make variables | Resolver flags `$(shell …)`, unresolved `$(VAR)`, conditionals, multiline declarations | Heuristic, not a complete Make parser |
| Path traversal / symlink | Enforced for approval targets (`check_path_safety`) | Other file-taking options not uniformly checked |
| Oversized inputs | Local, offline execution; no service exposure | No resource/size limits; potential slowdown |

Safe usage: pin inputs, check preflight, review evidence paths, avoid pointing the CLI at untrusted collateral.

## AI-related risks

- **Prompt injection in logs** — log text may contain instructions; any model output is **advisory only** and never crosses the approval boundary automatically.
- **Unsafe generated patches** — deterministic proposal rules bound changes; `NO_PROPOSAL` on no matching rule; human reviews the exact diff. A model can still influence reviewer judgment.
- **Over-trust** — no claim of general engineering competence. Live-AI diagnosis was not counted without credentials; no live-AI recovery is claimed.
- **Availability** — `SATTVA_MODEL_URL` unset or provider error → `SKIPPED_NO_CREDENTIALS`/`BLOCKED`; deterministic diagnosis is unaffected.
- **Leakage** — bundles are built for evaluation; treat them as possibly sensitive design data. Provider configuration is printed in redacted form by `live-diagnosis config`.

Mitigations that exist: advisory-only design, separate approval gate, bounded proposals, redacted config. Mitigations recommended (not implemented): strict output schemas, prompt segmentation/sanitization, independent deterministic patch checker, explicit data-handling review before sending bundles to an external provider.

## Credential handling

- No API keys, tokens, passwords, SSH keys, `.env`, or cloud credentials belong in the repository.
- Use environment variables; keep local configuration out of the repository.
- `SECURITY.md` recommends scanning staged diffs for `gho_`, `ghp_`, private-key headers, and personal absolute paths.
- `.gitignore` excludes common secret filenames but is not a substitute for reviewing `git diff --cached`.
- `live-diagnosis config` prints a redacted provider configuration.

No automated secret scanning is implemented in this milestone; add it as a future CI improvement.

## Related

`docs/security/THREAT_MODEL.md`, `docs/architecture/DIAGNOSIS.md`, `SECURITY.md`, `docs/research/LIMITATIONS.md`.
