# Threat model

Status: documentation-level audit; no new controls implemented. Sources verified: `scripts/sattva_approval.py`, `scripts/run_baseline_orfs.sh`, `scripts/manifest.py`, `scripts/diagnosis_agent.py`, `scripts/verify_run.py`, `scripts/live_diagnosis.py`, `state/approval_policy.json`, `config/sattva_manifest.json`.

## Framework and scope

A lightweight STRIDE-style categorization (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege) is applied to a research prototype that is an **CLI orchestrator**, not a network daemon or authentication service. Assets: run evidence, approval records, design collateral, tool binaries, credentials, and the integrity of historical results. Adversary: a malicious/malformed input, a compromised or careless local process, or an over-trusted model output. Trust boundaries are in `docs/security/TRUST_BOUNDARIES.md`.

## Threat register

| Threat | Scenario | Impact | Existing control (verified) | Evidence | Remaining risk | Recommended future improvement |
|---|---|---|---|---|---|---|
| Path traversal | Approval target contains `..` or relative path | Write outside allowed roots | `check_path_safety` rejects non-absolute paths, `..`, symlinked components, and targets outside `allowed_roots` (`sattva_approval.py:143-158`) | source | Low for approval path; unvalidated paths elsewhere not audited | Extend same check to all file-taking CLI options |
| Symlink manipulation | Target or parent is a symlink pointing outside boundary | Unauthorized file modification | Symlink check on target and all parents (`:150-154`) | source | TOCTOU window between check and write | Use `openat`/O_NOFOLLOW-style resolution |
| Unauthorized file modification | Patch applied to file outside permitted roots | Corrupted collateral | Allowed roots + resolution check (`:155-158`); atomic apply with `mkstemp`/backup/rollback (`:394-411`; `:341` is the 0600 ledger lock file) | source, policy | Relies on local FS and operator honesty | Signed policy + OS-level sandbox |
| Approval reuse | Same approval used for a second operation | Repeated unauthorized change | Append-only ledger + `check_ledger` rejects reused `operation_id` (`:181-196`) | source; ledger path is declared by `state/approval_policy.json` and generated at runtime (not tracked in the repo) | Ledger is local and append-only by convention | Cryptographically chained ledger |
| Hash mismatch / tampered patch | Patch changed after approval | Different change applied than reviewed | `patch_sha256` bound at create (`:441`) and rechecked at validate (`:234`) and apply | source | Hash integrity, not correctness | Sign approvals with a hardware/owner key |
| Stale fingerprint | Inputs changed since preflight | Recovery on wrong inputs | Manifest v2 pins revision, local patches, collateral/tool hashes; preflight fails on mismatch; approval binds fingerprint set | `config/sattva_manifest.json`, `:130-140` | Active profile only; inactive profiles unchecked | Extend to every consumed file |
| Cross-run contamination | Approval from run A used for run B | Wrong run "fixed" | Approval binds `source_run_id` + `decision_id`; validation requires `--run-id` | `:83,199-212` | IDs are not cryptographically authenticated | Bind to run evidence digest |
| Expired approval | Old approval used later | Change applied outside decision window | Optional `expires_at` parsed and enforced (`:223-229`) | source | Optional, not always set | Make required by policy |
| Unsafe rerun scope | Broad/contiguous-invalid scope | Unrelated stages rerun | `validate_scope`: known stages, no duplicates, contiguous, starts at earliest stage (`:161-178`) | source, policy | Scope still human-declared | Derive scope from evidence automatically |
| Fail-open verification | Missing evidence reported clean | False success | `verify_run.py`: missing evidence → `UNKNOWN`/`FAIL`, last DRT count, empty-report rule | `scripts/verify_run.py:12-20,37-38` | Rule set is benchmark-specific | Add more tool/report patterns |
| Malicious input files | Malformed `.lib`/`.lef`/SDC/netlist | Parser crash, misleading diagnosis | Read with `errors="replace"`, bounded regex scans; manifest hashes pinned collateral | diagnosis_agent, verify_run | Not a hardened parser; no fuzzing evidence | Fuzz inputs; strict schema validation |
| Malformed configuration | `$(shell …)`, unresolved vars, overrides | Wrong effective value | Config resolver flags ambiguous constructs; attempt-local overrides isolated | `:66-79` | Heuristic, not a full Make parser | Use a real Make AST |
| Prompt injection in logs | Log text instructs a model to emit unsafe patch | Unsafe patch proposed | Model output is advisory only; never applies/approves; human gate on exact diff | `pnr_cli.py:110-134`, `live_diagnosis.py` | Model may still mislead reviewer | Sanitize/segment prompts; output schema enforcement |
| AI-generated unsafe patch | Model proposes constraint relaxation | Unsafe change | Bounded proposal rules + approval gate; `NO_PROPOSAL` on no rule; no model in critical path by default | diagnosis_agent, pnr_cli | Model can influence human judgment | Independent deterministic patch checker |
| Shell execution risk | Untrusted input passed to shell | Command execution | Runner uses explicit env + `bash` on known script; no `shell=True` in audited approval path | `pnr_cli.py:45-56`, approval source | Whole runner not fully audited in this milestone | Full shell-quoting audit |
| Credential exposure | API key committed or logged | Account compromise | No credentials in repo; SECURITY.md scanning guidance; redacted provider config | `SECURITY.md`, `live_diagnosis.py config` | No automated secret scanning in CI | Add pre-commit secret scan |
| Dependency tampering | ORFS/tool binary swapped | Wrong results | Pinned revision + two patches + tool/collateral hashes, `--check` | manifest, `docs/REPRODUCIBILITY.md` | Supply-chain trust of upstream still required | Reproducible builds + signed artifacts |
| Tool compromise | Compromised OpenROAD/Yosys binary | False reports | Binary hashes pinned; evidence captures logs for cross-check | manifest, evidence | Hash pin detects change, not malicious original | Vendor verification / isolated build |
| Incomplete or misleading evidence | Missing log, stale report, first DRT count | False diagnosis/verdict | Evidence rules + last-count rule + missing≠pass | verify_run, EVIDENCE.md | Benchmark-specific patterns | Broader evidence schema |
| Unsafe recovery scope | Change to wrong corner/constraint | Invalid engineering result | No constraint relaxation rule; SDC change explicitly approved; originals preserved | `docs/engineering/SDC_TIMING.md`, approval | Human can still approve a bad change | Independent engineering review gate |
| Denial of service | Huge/malformed logs stall parsing | Workflow unavailable | Bounded scans; offline, local execution | diagnosis_agent, verify_run | No resource limits implemented | Add size/time caps |
| Repudiation | Actor denies approving a change | Accountability loss | Approval binds `approver`, IDs, ledger append | `:575-592`, ledger | Approver field is self-declared | Authenticated identities |

## Safe usage recommendations

1. Run only against the pinned control benchmark and pinned tools; do not bypass preflight.
2. Review the exact diff in `approve-view` before creating an approval; keep approval records and ledger.
3. Keep `SATTVA_MODEL_URL` unset unless live advisory diagnosis is explicitly wanted; treat all model text as untrusted.
4. Never store credentials in the repository; use environment variables and redacted `live-diagnosis config`.
5. Do not apply approvals across runs; do not reuse an approval ID.
6. Treat verification `PASS` as tool-level only; perform independent engineering validation.

## Non-claims

No claim of a hardened security boundary, authentication service, sandbox, fuzzed parsers, or signed approvals. This audit is documentation-level and does not add controls.

## Related

`docs/security/TRUST_BOUNDARIES.md`, `docs/security/INPUT_AND_AI_RISKS.md`, `docs/security/EVIDENCE_INTEGRITY.md`, `SECURITY.md`.
