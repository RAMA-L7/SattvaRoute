# REVIEW_LOG — engineering review history

> What was inspected · problems · risks · decisions · validation · reviewer conclusion · follow-up.
> Newest entry first.

## R-016 — T-SKILL-003 PS-001 methodology checklist (2026-11-23, orchestrator)

- **Inspected:** upstream experimental-design SKILL.md v1.5 at pinned SHA; `docs/EXPERIMENT_DESIGN_CHECKLIST.md`; catalog status honesty; protected artifact hashes.
- **Reviewer verdict:** ACCEPT WITH LIMITATIONS. All Fisher/structural principles faithfully represented; safety controls intact.
- **Findings fixed:** A3 falsely cited FDE-006U three-way equivalence as a no-op control (it was instrumentation-neutrality; report says no no-op arm) — corrected; A1 and A9 marked INFERRED where SattvaRoute translation is not upstream wording; A12 added for baseline immutability and scratch isolation.
- **Conclusion:** DRAFT checklist usable for FDE planning; no install, no active gate, all catalog statuses RECOMMENDED.
- **Follow-up:** publish; explicit adoption authorization still required.

## R-015 — T-SKILL-002 skill adoption research (2026-11-23, orchestrator)

- **Inspected:** Agents A–E reports; 183 local SKILL.md corpus, 7 external queries, 10 full-text external audits; proposed catalog wording and strip-lists.
- **Findings:** zero installs preserved; 5 RECOMMENDED methodology references with REQUIRED relabel (no MUST ADOPT/INSTALLED conflation); gap mapping corrected (causal attribution is not skill-solvable); local candidates compared; strip-lists hardened (no deletions, no protected-artifact edits, D-007 stays human); external counts from C §4 snapshot.
- **Decisions:** D-026; first adoption PS-001 experimental-design as a new separately-approved pre-run checklist, not an AGENTS.md edit.
- **Conclusion:** ACCEPT WITH LIMITATIONS; Agent E ACCEPT WITH LIMITATIONS; all five required fixes applied to catalog and report.
- **Follow-up:** publish; no installation without a new gate.

## R-013 — T-SKILL-001 skill discovery (2026-11-23, orchestrator)

- **Inspected:** Workstream A discovery, B requirements, C evaluation, D security audits; `.skills/` inventory, reports and validator; protected artifact hashes.
- **Findings:** 164 unique local skills; 11 evaluated; no REQUIRED skill. Review framework duplicates `REVIEW_LOG.md` and conflicts with approval gates; `find-skills` quarantined; `graphify` quarantined; `openroad-mcp` is an MCP tool, not a skill. C's graphify path detail corrected against A and direct inspection; disposition unchanged.
- **Decision:** D-025 — install ZERO skills. Binding rules in `.skills/README.md`; AGENTS.md intentionally unmodified (protected artifact).
- **Conclusion:** validator 11/11 PASS; KB verify PASS; immutable 9/9 PASS; no production change.
- **Follow-up:** independent review of inventory accuracy and security/scope compliance, then publication.

## R-014 — T-SKILL-001 independent review (2026-11-23, orchestrator)

- **Reviewers:** E (inventory/governance), F (security/scope). Both: ACCEPT WITH LIMITATIONS.
- **Verified:** 164 discovered / 11 evaluated / 0 installed counts consistent; zero-install recorded in all locations; 14 usage rules subordinate to governance; AGENTS.md unmodified (immutable 9/9 PASS); no placeholder folders; graphify path discrepancy honestly recorded; validator 11/11 PASS; no network install; HIGH-risk skill claims confirmed in source.
- **Findings resolved:** `scripts/publish_skill.sh` added to D-025/task board/handoff/logs; pending statuses updated; user decision point and Gate 7 definition recorded in `.skills/INSTALLATION_REPORT.md`.
- **Conclusion:** all gates satisfied; T-SKILL-001 DONE. Stop after this milestone; await explicit user selection before any additional skill integration.

## R-012 — T-KB-001 incremental Knowledge Base (2026-11-23, orchestrator)

- **Inspected:** Agent A audit, B schema review, C retrieval review, D workflow review, E safety review, F validation adjudication, G FDE inventory; all implemented code and tests.
- **Findings resolved:** `record_version`/`supersedes` correction path now works; unknown fields rejected; append chain + store-hash verification added; FAIL/inconclusive maturity cap; actionable-remedy guard (diagnostics cannot be recommended); reconsideration requires evidence references; `INSUFFICIENT_EVIDENCE` reachable; all ranking factors explained; publication allow/blocklist with post-copy hashes.
- **Accepted limitation:** provenance drift on `docs/decisions/DECISIONS.md` (D-024 appended after capture) — documented in `knowledge/PROVENANCE_DRIFT.md`; no FDE report changed. No maturity-4 record (no cross-design/signoff evidence).
- **Conclusion:** KB ACCEPTED WITH LIMITATIONS. All tests PASS (21/21 KB, 25/25 approval, 14/14 runner); verify 18/18 + chain, immutable 9/9.
- **Follow-up:** use KB for the next FDE; preserve append-only history; no production promotion.

## R-011 — FDE-007 Gate 1 remedy evaluation (2026-11-20, orchestrator)

- **Inspected:** four agent reports, FDE-006U artifacts, GDS/KLayout census, remedy options, validation plan, safety review.
- **Findings:** FDE-006U mechanism evidence re-verified; experimental broad M4 carve is a diagnostic counterfactual that frees 120 real M4 shapes + 92 pin shapes, so NOT a production remedy. GDS supports only narrow right-edge escape strips. R3 config is a no-op/suppression risk; R2 needs GDS/generator change; R4 refuted.
- **Decisions:** D-022 proposes R1-N (narrow GDS-derived per-pin M4 OBS corridor, scratch only) — PROPOSED, not approved. No implementation, flow run, waiver, or deployment authorized.
- **Conclusion:** Gate 1 COMPLETE; BLOCKED at Gate 2 pending explicit approval.
- **Follow-up:** approve exact R1-N geometry and validation gates, then scratch implementation and full-flow validation.

## R-010 — FDE-006U candidate attribution and OBS A/B review (2026-11-20, orchestrator)

- **Inspected:** four agent reports (including post-run adjudication), marker attribution patch, three equivalence logs, A/B logs, OBS control verification, source ODB and binary hashes.
- **Findings:** same binary `0d890431…` in both arms; single-variable M4 OBS carve verified (DEF round-trip byte-identical, M1/M2/M3/M5 unchanged); A: 9 candidates/0 accepted/sparse 0<3/DRT-0073; B: 3 candidates/3 accepted/sparse 3≥3/no DRT-0073; M5 markers persist in B, so M4 OBS is decisive while other violations contribute.
- **Decisions:** D-021 adopted — ROOT CAUSE ESTABLISHED (bounded, mechanism-level); no remedy approved.
- **Conclusion:** independent reviewer GO with scope limits and residual gaps recorded (no marker getSrcs(), no no-op arm, non-DEF properties not exhaustively diffed).
- **Follow-up:** separate approval for production remedy and full-flow DRC/timing validation.

## R-009 — FDE-006T link resource and candidate evidence review (2026-11-20, orchestrator)

- **Inspected:** four agent reports, kernel OOM counters, build/gate logs, equivalence logs, candidate-level debug output, OBS API probes.
- **Findings:** SIGKILL was external (not OOM); no resource or flag change needed; detached build succeeded; binary equivalence passed; nine `u_sram/clk` M4 candidates were generated and all rejected by planar/via DRC, leaving sparse count 0 < 3. Scratch OBS control blocked by absent safe Tcl API.
- **Conflict resolved:** Agent C's OOM label rejected in favor of Agent A's direct kernel evidence.
- **Decisions:** D-020 adopted — root cause remains PROBABLE (high confidence), not ESTABLISHED; no remedy approved.
- **Follow-up:** approved OBS-control mechanism or marker-geometry instrumentation, then repeat A/B.

## R-008 — FDE-006S native resumption review (2026-11-20, orchestrator)

- **Inspected:** four agent reports, WSL health checks, C: cleanup evidence, native workspace hashes, gate logs, build log.
- **Findings:** WSL healthy (no recovery needed); prior failure was transient ext4/journal I/O; native workspace source patched hash `305230b9…`; strict offline gate RC=0; build reached 13,480/13,482 then SIGKILL RC=137 during final ThinLTO link, no binary, no OOM marker.
- **Decisions:** D-019 adopted (BLOCKED/INCONCLUSIVE); no remedy approved; no speculative retry.
- **Conclusion:** environment blocker at final link; candidate-level root cause remains unproven, status stays PROBABLE.
- **Follow-up:** approved build environment with enough memory for the link, then build → equivalence → A/B.

## R-007 — FDE-006R dependency unblock review (2026-11-19, orchestrator)

- **Inspected:** four agent reports, `debugfs` image inventory, Go SDK pin/hash, authorized fetch result, offline dry-run logs, corrected patch and dry-run result, build log.
- **Findings:** local image recovery resolved `rules_go`/`bazel_features`; only Go SDK was absent and was fetched with explicit authorization and exact hash match; strict `--nofetch` dry-run RC=0; original patch needed correction and was replaced by a valid 14-point target-only diff; build blocked by environment (drvfs linking, then WSL process-spawn failure).
- **Decisions:** D-018 adopted (BLOCKED/INCONCLUSIVE); no remedy approved; no system repair attempted.
- **Conclusion:** dependency strategy was valid; environment failure prevented candidate-level evidence.
- **Follow-up:** resume in native WSL workspace after environment health returns.

## R-006 — FDE-006 instrumented FlexPA investigation (2026-11-19, orchestrator)

- **Inspected:** four agent reports, isolated source copy, production source/binary/ODB hashes, Gate 2 dry-run log, proposed patch design.
- **Findings:** pipeline and instrumentation points established from source; expected candidate set reconstructed geometrically; build blocked offline because `rules_go++go_sdk+go_toolchains` is not cached and the build image cannot be mounted; no candidate-level runtime data.
- **Conflict resolved:** Agent D's "373 dirty source files" vs Agent C's clean claim — direct `git -C /mnt/d/tools/src/OpenROAD status --porcelain | wc -l` = 2; the larger count came from the copied tree being evaluated against the enclosing SattvaRoute repo.
- **Decisions:** D-017 records BLOCKED/INCONCLUSIVE; root cause remains PROBABLE; no remedy approved.
- **Conclusion:** stop condition met; do not fetch dependencies, install toolchains, or apply a fix without separate approval.
- **Follow-up:** provide offline Bazel repo cache or a prebuilt instrumented binary, then rerun Gates 1–4.

## R-005 — FDE-005 controlled FlexPA diagnostic review (2026-11-19, orchestrator)

- **Inspected:** four agent reports, `reports/EXPERIMENT_GO.md`, both arm logs/Tcl scripts, manifests, source ODB before/after proof.
- **Findings:** source ODB `35bff121…` unchanged; scratch copies hash-identical, distinct inodes, non-symlink; A/B logs differ only by the echoed command; both arms report the single aggregate unmet condition `At least 3 sparse access points` and DRT-0073; via-in-pin M4 control had no effect.
- **Decisions:** D-016 finding adopted; root cause remains PROBABLE, not upgraded (no candidate-level rejection data).
- **Conclusion:** experiment executed safely and is reproducible; diagnostic ceiling is a tool limitation, not an experiment defect.
- **Follow-up:** instrumented candidate-level AP diagnostic requires separate approval.

## R-004 — FDE-004 DRT-0073 root-cause review (2026-11-19, orchestrator)

- **Inspected:** four parallel read-only agent reports; FDE-003 run `5_1_grt.log/.json`, `4_cts.odb`, macro LEF/GDS/Liberty, `macro_placement.tcl`, ASAP7 track/via definitions, installed OpenROAD FlexPA source.
- **Findings:** `clk` single M4 pin 0.084×0.024 µm, center exactly on M4 track; full-macro M1–M5 OBS with no carve-outs; one geometric via candidate but M3/M5 halves inside OBS; FlexPA evaluated the pin and all APs were filtered, exact stage unproven. Placement legal and on-track; Snapper bypass irrelevant; grid/classification/D-014 refuted.
- **Decisions:** D-015 finding adopted (root cause PROBABLE); no remedy approved.
- **Validation:** LEF↔GDS↔Liberty↔ODB agreement; four independent agents converged on mechanism class.
- **Conclusion:** ROOT CAUSE PROBABLE; missing per-candidate AP diagnostics prevent HIGH certainty on exact filter stage.
- **Follow-up:** scratch-copy FlexPA AP diagnostic with via-in-pin control, only after approval.

## R-003 — Milestone 1C-R DRT-0305 root-cause review (2026-11-18, orchestrator)

- **Inspected:** four independent subagent reports (`reports/agent_{A,B,C,D}_*.md`); installed OpenROAD source (`drt/src/io/io.cpp:1031-1070`, `odb/src/db/dbTypes.cpp:392-397`, `sta/verilog/VerilogReader.cc:117,2019-2020`, `dbSta/src/dbReadVerilog.cc:768-773`, `src/OpenRoad.tcl:367-413`); ODB DBs across stages; all preserved route logs and `preflight.txt`; a read-only in-memory probe of `$net setSpecial`.
- **Findings:** DRT-0305 is a DB-import guard (`supply sigtype && !isSpecial`) raised by `pin_access`, not a routing algorithm failure. `zero_` is a constant-tie net (six macro SIGNAL sinks) typed GROUND without SPECIAL, caused by `SYNTH_NETLIST_FILES` bypassing `hilomap`. `set_special_nets` does not exist. D-013 failed for four independent reasons (invalid command, wrong `D:\tools` checkout, unreachable insertion after `pin_access`, no preserved evidence). PDN/VDD/VSS and DB consistency are correct.
- **Risks:** marking `zero_` SPECIAL unblocks global routing but leaves six macro signal inputs without physical tie geometry — potential detailed-route opens/DRC. Must be disclosed, not hidden.
- **Decisions:** D-013 retired as FAILED; D-014 proposed (OpenDB `$net setSpecial` in mirror before `pin_access`), approval required.
- **Validation:** four independent agents converged; source + DB + execution-log + runtime-probe evidence; primitive probe `rc=0`, `isSpecial` 0→1.
- **Conclusion:** root cause adjudicated with HIGH confidence; no fix applied pending approval.
- **Follow-up:** approval gate; controlled run with new run ID; report-level verification per D-007.

### R-003 addendum — D-014 experiment (2026-11-18T22:47+05:30)
- **Inspected:** `runs/orfs_baseline_20261118T171712Z/evidence/preflight.txt`, `stage_route.log`, `work/logs/.../5_1_grt.log`; mirror and `D:\tools` hashes.
- **Findings:** D-014 applied only to the mirror (hash 3968898c…→cd86b587…), `D:\tools` unchanged, preflight shows the modified mirror. DRT-0305 eliminated; design imports 3 snets (was 2), confirming `zero_` SPECIAL. New blocker DRT-0073 `No access point for u_sram/clk` at pin access (`FlexPA_acc_point.cpp:1524–1533`), with DRT-0419 warnings for macro D/Q pin centers. No `5_*.odb`/`route.guide`.
- **Conclusion:** D-014 is a verified fix for DRT-0305 but is NOT a completion claim — global routing is blocked by a distinct macro pin-access issue.
- **Risk/next:** do not stack a second fix; new decision ID and evidence required for DRT-0073; routing/extraction/timing remain NOT EVALUATED.

## R-001 — Milestone 0 environment & toolchain review (2026-11-18, orchestrator)

- **Inspected:** Windows/WSL/hardware; `D:\tools\EDA_TOOL_REGISTRY.md`; ORFS clone; ASAP7 platform; OpenFinRAM source (flow order, Calibre touchpoints, Yosys requirements).
- **Findings:**
  - WSL sees only 7.6 GiB (default 50% cap, no `.wslconfig`) — risk for large designs, accepted for small benchmark (D-006).
  - ORFS `SYNTH_NETLIST_FILES` confirmed in clone (`flow/scripts/synth_preamble.tcl:17-25`).
  - ASAP7 platform in clone is complete for PnR but fakeram macros have **no GDS** (abstract-only) — acceptable fallback, not primary benchmark.
  - OpenFinRAM hard-fails on missing Calibre `v2lvs` at `openroad_manager.cpp:159`, **after** GDS (line 128) and **before** nothing else critical; LVS already non-fatal in `main.cpp:127`.
  - OpenFinRAM `sram_control.v:50` needs Yosys ≥0.55 (multi-dim packed array ports); system Yosys 0.33 fails with parse error at `sram_control.v:50`.
- **Decisions:** D-003 (ORFS path), D-004 (v2lvs patch), D-005 (yowasp shim), D-006 (WSL RAM).
- **Validation:** OpenFinRAM full run EXIT=0; GDS top cell `sram_x4x4x1` (65 cells, dbu 0.00025); LEF CLASS BLOCK 3.672×13.608 µm, 22 pins; Liberty present (estimated).
- **Conclusion:** Environment is sufficient for Milestone 1 baseline. Macro flow is reproducible via `scripts/gen_sram_macro.sh`.
- **Follow-up:** (1) controller RTL + netlist provenance; (2) first ORFS run may expose OpenROAD-version or PDN incompatibilities — treat as evidence, not failure; (3) macro Liberty is estimated — document as limitation.

## R-002 — OpenFinRAM v2lvs patch review (2026-11-18, orchestrator)

- **Inspected:** `src/openroad_manager.cpp:159-166` patch (fatal→warning).
- **Problem addressed:** commercial Calibre absent; SPICE output feeds LVS only.
- **Risk:** controller SPICE for LVS is silently absent — mitigated: LOGW emitted at run time (log line 48-49 of run) and LVS itself reports non-fatal skip; signoff LVS out of scope for M1.
- **Conclusion:** Acceptable for Milestone 1. Must be disclosed in every baseline report (see REPORT_LOG limitations).
