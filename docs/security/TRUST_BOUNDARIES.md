# Trust boundaries

Status: documentation-level analysis. See `docs/security/THREAT_MODEL.md` for the full threat register.

## Boundaries

### 1. Engineer ↔ SattvaRoute
The engineer supplies commands, approvals, and judgment. SattvaRoute supplies evidence-bound proposals and verdicts. The engineer is trusted to approve only reviewed changes; the tool is trusted only to display and apply the exact bound patch.

### 2. SattvaRoute ↔ EDA flow (ORFS/OpenROAD/Yosys)
The runner launches pinned external tools. Tool binaries and collateral are identified by hash; revision and local patches are pinned. Tool *correctness* is not asserted — reports are cross-checked against evidence.

### 3. SattvaRoute ↔ Evidence
Evidence is captured by the runner and read by diagnosis and verification. Evidence is treated as untrusted content: log text is parsed with bounded regexes and `errors="replace"`, never executed.

### 4. Proposal ↔ Approval (human gate)
A proposal crosses into an actionable change **only** through a human-created approval record. This is the most important boundary: no command in the CLI manufactures approval.

### 5. Approval ↔ Apply/Execution
`validate` must pass before apply; `check_path_safety`, `validate_scope`, hash checks, ledger, and expiry enforce the boundary. Apply is atomic with backup and restore on post-apply hash failure.

### 6. Recovery ↔ Original state
Recovery runs in an isolated attempt; baseline, original collateral, and history are not modified in place.

### 7. Verification ↔ Everything else
Verification reads runs and produces a verdict. It never applies changes and never modifies the inspected run.

### 8. Optional model provider ↔ SattvaRoute (outside the control path)
A configured model may produce advisory text only. Its output never crosses the approval boundary automatically. Without credentials the provider is unavailable and deterministic diagnosis still works.

## Data classification

| Data | Trust level | Handling |
|---|---|---|
| Approval records / ledger | High integrity | Append-only, hash-bound, reviewed |
| Manifest / fingerprint | High integrity | Checked by preflight; fails closed on mismatch |
| Run evidence / logs | Untrusted content | Parsed, never executed; `errors="replace"` |
| Model output | Untrusted | Advisory only; human gate |
| Tool binaries / collateral | Pinned, externally trusted | Hash-verified |
| Credentials | Secret | Environment only; never in repo |

## Non-claims

No network perimeter, authentication service, multi-tenant isolation, or sandbox is implemented. This is a local research CLI.

## Related

`docs/architecture/ARCHITECTURE.md`, `docs/security/SAFETY.md`, `docs/security/THREAT_MODEL.md`.
