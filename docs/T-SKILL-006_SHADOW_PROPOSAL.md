# Shadow-pilot target proposal P-SHADOW-001 (NOT APPROVED, NOT EXECUTED)

- **Date:** 2026-11-23
- **Status:** DRAFT proposal reconstructed from already-documented next-step requirements; **no decision, no approval, no execution**. Used only as a T-SKILL-006 shadow assessment target.
- **Source of requirements:** `docs/FDE-007_REMEDY_EVALUATION.md` §"Required for any new proposal";
  `logs/sessions/FDE-007_S001_handoff.md` §Next; D-022/D-023 outcomes.

## 1. Purpose (diagnostic only)

Collect the evidence that FDE-007 lacked before any further DRT-0073 geometry remedy is proposed:
1. marker source provenance (`getSrcs()`) for the planar `Short`, `Metal Spacing`, `Lef58EolKeepOut`
   and VIA45/M5 `Short` markers on `u_sram/clk`;
2. a read-only KLayout GDS census at the 2 nm sliver coordinate and at the metal-spacing bands;
3. an all-pin AP survey for all 12 M4 signal pins (not only `clk`);
4. a canonical DB diff and an identity/no-op control for any future change; and
5. a quantitative mechanism for the spacing/EOL rejections.

**Claim scope:** mechanism attribution and evidence completeness only. This proposal asserts **no
causal contrast** and proposes **no remedy geometry**, no production change and no full-flow run. Any
remedy would need a separate decision and approval gate.

## 2. Planned arms (not launched)

| Arm | Configuration | Purpose |
|---|---|---|
| A — baseline | original ODB `35bff121…`, unmodified LEF/OB S, production binary `c1b90e0a…` | reference measurement |
| B — instrumentation identity | instrumented diagnostic binary with instrumentation gate **OFF**, original OBS | instrumentation-neutrality check; must match A except script path |
| C — instrumented measurement | same instrumented binary with `getSrcs()` logging **ON**, original OBS | marker provenance and candidate-level evidence |

All arms would use the same source ODB SHA-256 `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1`,
the same scratch-isolated working directory and the same pinned config. Binary, ORFS/OpenROAD commit,
Yosys/ABC versions and shims would be hashed and recorded per arm. Run order would be assigned by a
pre-recorded deterministic rule (`sha256(decision_id + run_tag)` sort).

## 3. Pre-registered acceptance bar (draft, to be fixed before any approval)

- Every marker type listed in §1 has at least one `getSrcs()` attribution record, or is explicitly
  labelled UNKNOWN with reason.
- GDS census covers the sliver bounding box `(4703,16560)-(4705,16584)` and the observed spacing bands;
  each shape recorded with layer/datatype and net where resolvable.
- All 12 M4 signal pins reported (accepted/rejected AP counts, sparse counts); pins not reached are
  NOT_RUN, not silently omitted.
- Arms A vs B differ only by script path/instrumentation wrapper, verified by log diff; otherwise
  instrumentation is treated as non-neutral and the run is STOPped.
- No OBS geometry, LEF, GDS, netlist, RTL, SDC, PDN, config or placement modification.
- D-007 report-level verification with a named independent reviewer; no PASS from `rc=0`.
- Outcome labels limited to PASS / FAIL / INCONCLUSIVE / BLOCKED / NOT_RUN.

## 4. Known constraints and risks (to be assessed)

- The instrumented diagnostic binary previously required a build that was blocked (FDE-006/006R/006S)
  and only completed detached in FDE-006T; feasibility must be proven before execution.
- `getSrcs()` availability in the installed OpenROAD build is NOT VERIFIED.
- GDS census tooling (KLayout Python) is available but the exact layer/datatype mapping must be restated.
- N=1 run per arm; AP candidates and DRC markers are sub-units, not independent replicates.
- No remedy family has been selected; family aliasing must not occur (FDE-007 R1-N/R1-N-W = one
  `M4_OBS_CORRIDOR` family).

## 5. Explicit non-goals

No EDA execution, no remedy implementation, no production promotion, no KB record change, no approval
bypass, no checklist activation. This document is a shadow-pilot input only.
