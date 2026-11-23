# T-SKILL-008 shadow proposal P-SHADOW-002 (NOT APPROVED, NOT EXECUTED)

- **Date:** 2026-11-23
- **Status:** genuinely new, unapproved, unexecuted proposal. Shadow assessment input only.
- **Distinct from:** P-SHADOW-001 (DRT-0073 marker-provenance diagnostic). This proposal targets the
  **DRT-0419 non-fatal M3 D/Q pin-center advisory**, a different mechanism documented in
  `docs/FDE-004_DRT0073_ROOT_CAUSE_INVESTIGATION.md` §5/§6 (8 warnings on `5_1_grt.log:36-43`; D/Q
  centers 3–4 DBU off M3 tracks; `io_parser_helper.cpp:926-929`).

## 1. Question and claim scope

**Question:** Does aligning the macro `D[*]/Q[*]` pin centers to the nearest M3 routing tracks (3–4 DBU
scratch placement adjustment) eliminate the DRT-0419 advisory, and does that change pin-access or
placement legality outcomes?

**Class:** causal diagnostic (two arms with a single deliberate contrast). It is **diagnostic only**:
no production remedy is proposed, no production LEF/GDS/placement/config is changed, and no full-flow
success is claimed. Any future remedy would require a separate decision and approval gate.

## 2. Arms (not launched)

| Arm | Configuration | Role |
|---|---|---|
| **A — control** | original baseline `runs/orfs_baseline_20261119T131025284719666Z_9263` (ODB `35bff121…`), unmodified `macro_placement.tcl`, production binary `c1b90e0a…` | concurrent, unmodified control |
| **B — treatment** | scratch copy of the design tree; only `macro_placement.tcl` D/Q target coordinates adjusted by the measured 3–4 DBU to align pin centers with M3 tracks; same binary, ODB, LEF/GDS/Lib, config, SDC, PDN, D-014 patch | single-variable treatment |

Both arms run from separate isolated scratch directories under `experiments/`, with unique run IDs and
hashed manifests. Arm order is assigned by a pre-recorded deterministic rule; the resulting order and
inputs are recorded before execution.

## 3. Pre-registered acceptance bar (draft — to be fixed at a real gate)

- DRT-0419 census per arm (count, pin name, exact bbox/message) from `5_1_grt.log`.
- Per-pin table: `D[0..3]/Q[0..3]` center coordinates, nearest M3 track, signed offset in DBU.
- Placement legality (`check_placement` violations), MPL-0005 status, AP counts and DRT-0073 status
  recorded per arm — these are **guardrail** outcomes, not success claims.
- N = 1 independent run per arm; the 8 DRT-0419 markers and per-pin measurements are **sub-units**,
  never replicates. No claim beyond these two runs.
- Outcome labels limited to PASS / FAIL / INCONCLUSIVE / BLOCKED / NOT_RUN; no `rc=0` PASS; D-007
  report-level verification with a named reviewer at execution.
- No change to production files, RTL, netlist, SDC, LEF/GDS/Lib, PDN, routing layers, track grid, via
  rules, or the D-014 patch.

## 4. Known risks / dependencies (to be assessed by agents)

- **Measurement capability:** extracting exact pin-center coordinates and DRT-0419 bboxes from the
  installed OpenROAD logs must be verified; the toolchain may only emit aggregate advisory counts.
- **Single-variable validity:** scratch placement edits may move the whole macro (affecting `clk` and
  all 22 pins), not only D/Q centers; the modification digest must describe the exact scope.
- **Confounders:** D-014 in-memory `setSpecial`, WSL memory/swap, supervisor mode, run order, binary and
  ODB hashes, scratch cleanliness, KLayout/GDS tooling version if geometry is inspected.
- **Remedy-family separation:** no family is selected; D-012 (`-exact` placement) is a historical
  decision, not a remedy family. Any future geometry remedy must run `sattva_kb.py assess` /
  `duplicate_check` with the authoritative `relationships.remedy_family` key.
- **Review/approval:** this is a shadow-only proposal; there is no approval, no named independent
  reviewer and no pre-run sign-off. R2's stage/shadow dispositions must handle this without forcing
  false FAILs and without silently passing it.
- **Feasibility:** prior full runs complete stages through `route` in ~90 s, but placement edits may
  alter floorplan/place legality; preflight and a bounded execution plan are required at a real gate.
- **No-remedy boundary:** evidence suggesting a placement remedy must trigger STOP and a new proposal.

## 5. Explicit non-goals

No EDA execution, no remedy implementation, no production promotion, no KB/approval change, no R2
activation or revision. Shadow assessment only.
