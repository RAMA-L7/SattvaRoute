# T-SKILL-008 — Dated R2 Shadow Assessment (IMMUTABLE RECORD)

- **Assessment date:** 2026-11-23
- **Status:** SHADOW ONLY — R2 is DRAFT/INACTIVE; nothing here approves, launches or enforces anything.
- **Target:** P-SHADOW-002 (`docs/T-SKILL-008_SHADOW_PROPOSAL.md`, SHA-256
  `185ecee256385d5516fe2b829f0b7670eea585acf40f6c1f4f6497033ff0d3c9`) — genuinely new, unapproved,
  unexecuted; DRT-0419 pin-center causal diagnostic, distinct from P-SHADOW-001.
- **Instrument:** R2 (`docs/EXPERIMENT_DESIGN_CHECKLIST.md`, SHA-256
  `6900ebc8b17821f7b1bb30f29224d0eb120042fd5e392dbbf42046877ba4cb9d`).
- **Assessors:** Agent A (R2 application), Agent B (blind independent validity), Agent C (usability);
  coordinator adjudicated.
- **Immutability:** dated record; do not edit. Corrections go into the final report or a new assessment.

## 1. Class determination

R2-K class = **`causal diagnostic`** (two arms with a deliberate contrast). Therefore A3/A4/A6 apply,
A13 requires a full cost cap, and the mechanism-only/no-remedy bounded-resource exception does **not**
apply — Agreement among all three agents.

## 2. Adjudicated A1–A17 dispositions

| Item | Stage | Disposition | Evidence / adjudication |
|---|---|---|---|
| A1 | design | **PASS** | Question, unit (one run ID/arm), response and claim scope stated; sub-units not called replicates. A/B/C agree. |
| A2 | design | **PASS** | N=1 per arm; 8 DRT-0419 markers and per-pin measurements are sub-units; no inference beyond N=2. A/B/C agree. |
| A3 | design (concurrence at approval) | **PARTIAL** | Arm A is labelled "concurrent" but defined by a *historical* run; no modification-digest identity statement. R2-F: only a digest equal to approved baseline qualifies; prior historical run is not a concurrent control. Flips to FAIL/STOP if the historical artifact is reused. A PARTIAL, B PARTIAL/UNKNOWN — adjudicated PARTIAL with hard gate. |
| A4 | design | **PARTIAL** | No `macro_placement.tcl` digest; proposed D/Q-only edit may move the whole macro (all 22 pins incl. `clk`) — confound. B's "same ODB vs placement change" contradiction is valid and actionable. Digest required before execution. |
| A5 | design | **PARTIAL** | Nuisance factors listed in risks but no pinned hashed table or A14 cross-reference. |
| A6 | design | **PASS** | Deterministic order rule committed; resulting order/values recorded before execution. |
| A7 | design | **N/A** | **Adjudicated:** no *remedy-family value* appears in the proposal; the mention of the schema field name `relationships.remedy_family` is not a family. R2-H N/A therefore stands. B's PARTIAL concern concerns the placement-shaped treatment, which is an A4/A13 issue, not a named family. C's ambiguity (value vs field name) is recorded as an R3 clarification. Latent obligation: if any family value (including a placement family found in the KB) is named, run `assess`/`duplicate_check` with verbatim key. |
| A8 | design | **PARTIAL** | Bar draft "to be fixed at a real gate"; no fixed hash list or numeric thresholds; resolution tied to A17. |
| A9 | design / post-run outcome DEFERRED | **PARTIAL** | D-007 invoked and `rc=0` PASS rejected; no named reviewer; merged §B reviewer row not populated. |
| A10 | design plan; record at execution/post-run | **DEFERRED** | Pins named, but macro-edge position, NOT_RUN labels for unevaluated pins and no-cross-pin-generalisation statement missing at design. Stage-appropriate DEFERRED with named artifact/owner. |
| A11 | design fields; preflight PASS at execution | **PARTIAL** (+ nested UNKNOWN API probes → STOP for dependents) | ~90 s historical runtime noted, but no FDE-001 preflight fields/owner, ceiling, supervised/detached mode, timeout/escalation or detached contingency (FDE-006/006R/006S/006T). Preflight PASS correctly DEFERRED; API probes are NOT deferrable. |
| A12 | design + post-run ((b) DEFERRED) | **PARTIAL** | Baseline run/ODB/binary named but hashes truncated; no `verify-immutable` 9/9 result, exact scratch path or `allowed_roots` mirror hash. |
| A13 | design | **PARTIAL** | Causal diagnostic → full cost cap required; only bounded-resource/no-remedy STOP present. Exception correctly denied by R2-D/R2-K. |
| A14 | design | **PARTIAL** | No full binary SHA, ORFS/OpenROAD commit, Yosys/ABC, shims, WSL supervisor mode, KLayout/Python version or layer/datatype map. |
| A15 | design/approval | **DEFERRED-SHADOW** | No approval, no named reviewer/COI/sign-off. R2-E explicitly permits this; a missing sign-off is not NO in shadow. At a real gate, absence = NO. A/B/C agree. |
| A16 | reference | **N/A (gate)** | Demoted reference; no patch generated in shadow. |
| A17 | design | **UNKNOWN → STOP for dependent items A1/A8/A11** | Proposal admits exact pin-center and DRT-0419 bbox extraction unverified; FDE-004 §5 and D-016 show aggregate-only tool behavior. R2-J: no PASS, no DEFERRED for a required capability. A/B/C agree — highest-value catch. |

**Totals:** PASS 3 · PARTIAL 9 · DEFERRED 1 · DEFERRED-SHADOW 1 · N/A 2 · UNKNOWN 1 (17 items).

## 3. Detected design weaknesses (actionable)

1. **A17 capability STOP (critical):** run read-only probes for pin-center/bbox extraction; if only
   aggregates exist, narrow the bar at design as a recorded deviation or STOP.
2. **A3 control identity:** rewrite Arm A as a fresh concurrent run with modification digest equal to
   approved baseline; name the historical run only as source of pinned inputs; record digest/hashes/window.
3. **A4 single-variable scope:** attach the `macro_placement.tcl` diff proving D/Q-only scope; resolve
   "same ODB vs placement change" contradiction; address whole-macro confound with `clk`.
4. **A13 class mismatch:** add numeric cost cap and authoriser; stop using mechanism-only framing for a causal contrast.
5. **A5/A8/A11/A12/A14 hygiene:** hashed nuisance table, fixed bar + hash list, preflight fields/owner,
   full SHA-256s, `verify-immutable` 9/9, scratch path, `allowed_roots` mirror hash, full toolchain manifest.
6. **A8/A9/A10/A15 hygiene:** populate merged reviewer row, add macro-edge/NOT_RUN labels, no-cross-pin
   generalisation, DEFERRED D-007 outcome.

## 4. R2 effectiveness observations (single prospective shadow only)

- **Material improvement demonstrated:** R2-A/E avoided false FAILs for shadow-stage reviewer/preflight
  (A15 DEFERRED-SHADOW, A11/A12(b)/A16 DEFERRED); R2-F drove a concrete A3 correction; R2-J exposed
  the load-bearing A17 capability gap before approval; R2-D/K correctly denied the no-remedy cost-cap
  exception for a causal contrast. Guidance was **actionable** (quoted items mapped to five corrections).
- **Not demonstrated:** prevention of a real failure; no experiment was run. No effectiveness claim
  beyond this single prospective shadow assessment.
- **Usability defects found (Agent C):** non-atomic DEFERRED can let design-stage sub-checks escape
  (A11 probe naming, A12(b) full SHA); A7 trigger ambiguous (family value vs schema field name); class
  distinction is an honour system with no self-consistency validator; missing criteria for whole-macro
  vs per-pin placement scope, M3 track math, DRT-0419 bbox derivation, D-014 parity, design-tree identity,
  KLayout trigger scope. Nine R3 recommendations supplied as proposals only — no R3 revision made.

## 5. Disposition

**Shadow-viable with one hard blocker (A17 UNKNOWN → STOP for dependents) and six design-stage
corrections.** No execution, approval, activation, R3 revision or production change authorized.
