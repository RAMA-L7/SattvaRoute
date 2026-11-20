# Session Handoff — FDE-006U S001

- **Task:** T-FDE-006U — Candidate rejection attribution and controlled OBS validation
- **Date:** 2026-11-20
- **Agent:** orchestrator (Hy4 flash Free) + Agents A/B/C/D (read-only analysis + independent review)
- **Safe for another agent to continue:** YES — lock released; no production change.

## Verified state

- Publish HEAD `06f1a76` = remote at start.
- Source ODB `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` unchanged.
- Production binary `c1b90e0a…` unchanged; FDE-006T reference `9c0ed727…` preserved.

## Work completed

- Two log-only insertions in `FlexPA_acc_point.cpp` (marker type/id/layer/bbox/stage associated with candidate), source `305230b9…` → `0fc94a9d…`.
- Separate diagnostic binary `0d890431065688930e8b140cb644e304a0a3a6beeaf32b2cff762a8aa000d33d`.
- Three-way equivalence PASS (prod / old diag / new diag debug-off identical after path normalization).
- Experiment A (new binary, original OBS): 9 M4 candidates, 107 marker records, 0 accepted, sparse 0<3, DRT-0073, rc=1. Marker types: M4 `Short`, `Lef58EolKeepOut`; VIA45 `Short`, `Metal Spacing`, `Lef58SpacingEndOfLine`.
- Experiment B (same binary, scratch M4 OBS window carve, verified single-variable via byte-identical DEF round-trip): 3 candidates, 13 markers, 3 accepted, sparse 3≥3, DRT-0073 absent, rc=0.

## Verdict

**ROOT CAUSE ESTABLISHED** (bounded, mechanism-level): full-body M4 master OBS blocks planar escape of `u_sram/clk`; M5 OBS, thin-pin EOL and metal spacing are contributing. Scope: `pin_access`, this ODB/LEF/toolchain only. Independent reviewer GO with residual gaps recorded. D-021 adopted; **no fix approved**.

## Residual gaps

No marker `getSrcs()` provenance (spatial attribution only); no separate no-op control arm; non-DEF ODB properties not exhaustively diffed; unpatched-control build byte-match inherited from earlier evidence.

## Next

Separate approval required for any production remedy (LEF OBS / pin geometry / via rules) and full-flow DRC/timing validation. No recovery or routing run authorized here.

Report: `docs/FDE-006U_CANDIDATE_REJECTION_ATTRIBUTION_AND_OBS_VALIDATION.md`.
