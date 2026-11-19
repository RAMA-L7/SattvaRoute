# Session Handoff — FDE-004 S001

- **Task:** T-FDE-004 — DRT-0073 macro pin-access root-cause investigation
- **Date:** 2026-11-19
- **Agent:** orchestrator (Hy4 flash Free) + Agents A/B/C/D (independent, read-only)
- **Safe for another agent to continue:** YES — lock released; no in-progress edits; all evidence preserved.

## Starting state

- Publish `d273077` = remote HEAD; live tree had expected uncommitted engineering records.
- Primary evidence run `orfs_baseline_20261119T131025284719666Z_9263` (FDE-003 validated): route rc=2, DRT-0073, no routed DB.
- D-014 patch `cd86b587…` present in mirror; `D:\tools` copy `3968898c…` unchanged.

## Findings (verified)

- `clk`: single M4 RECT 0.084 × 0.024 µm, local (3.534,8.376)–(3.618,8.400), absolute (4.764,16.560)–(4.848,16.584) µm at R0 placement (1.230,8.184); LEF/GDS/Liberty/ODB agree. Net `clknet_1_0__leaf_clk`; sigtype CLOCK, non-special.
- Center y=16.572 is exactly M4 track #345 (0 DBU error); M3 tracks at x≈4.797/4.833 cross the pin.
- OBS: five full-macro M1–M5 rectangles, no carve-outs; the only geometric via candidate (VIA34/VIA45 at x≈4.797) has M3/M5 halves inside OBS.
- FlexPA evaluated `clk` and all access-point candidates were filtered (DRT-0073); DRT-0419 on M3 D/Q is a different, advisory mechanism; D/Q AP success unproven.
- Placement legal, macro LOCKED, all M4 centers on-track; Snapper bypass (`-exact`) not causal.
- DRT-0305 absent; D-014/`zero_` unrelated to `clk`.

## Verdict

**ROOT CAUSE PROBABLE** — thin M4 `clk` pin over full-macro M1–M5 OBS leaves no legal via/escape access point. Exact FlexPA filter stage NOT EVALUATED (no candidate-level diagnostics). Confidence: HIGH for mechanism class, MEDIUM-HIGH for specific OBS/via mechanism.

## Limitations / missing evidence

Per-candidate AP dump with rejection reasons; OBS box intersection at via site; AP status of other pins; controlled via-in-pin / scratch-OBS comparison; OpenROAD source-revision pinning.

## Next action (requires approval)

New decision (e.g. D-016) for a scratch-copy `pin_access` diagnostic with `set_debug_level DRT pin_access 1` and explicit via-in-pin control. No design/config change, no full flow. Do NOT begin a remedy or another baseline.

Full report: `docs/FDE-004_DRT0073_ROOT_CAUSE_INVESTIGATION.md`. Decision record: D-015 (finding adopted, no remedy approved).
