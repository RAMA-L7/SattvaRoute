# T-ENGINEERING-010 — Independent Review and Coordinator Adjudication

- **Agents:** A (instrumentation/replay), B (independent audit), C (static EOL/GDS).
- **Coordinator:** verified primary artifacts, applied pre-registered rules, adjudicated.

## 1. Agent verdicts

| Agent | Verdict | Main result |
|---|---|---|
| A | COMPLETE | patch, build, equivalence and full replay executed within approval; 107 MARKER/PROV pairs |
| B | ACCEPT WITH LIMITATIONS | patch/build/equivalence independently verified; F1: PROV lacks aggressor rect/net and OBS tag |
| C | analysis complete | EOL envelope quantified; GDS sliver has zero foreign-net 40/0 |

## 2. Coordinator verification (actual)

- Patch hash `92ef2aac…`, source `0fc94a9d…→0815de7d…`, new binary `7461d0d0…`, original binary preserved `0d890431…`.
- Diff: 66 additions, 0 removals; dry-run RC=0.
- Census recomputed: arm_a 0/0, arm_c 0/0, arm_b and full 107/107 MARKER/PROV; DRT-0073=2 and DRT-0305=0 in full run.
- Sample PROV: victim `clknet…`, aggressor `u_sram#3:56` — macro/OBS object.
- Production binary `c1b90e0a…` and frozen ODB `35bff121…` unchanged.

## 3. Disagreements and limitations reconciled

1. **Agent A's source-authorship note vs primary hashes:** the coordinator asserts only that the diff matches the mandate and hashes verify; authorship is not claimed (B-F2).
2. **RC=137 build:** stalled client died before compile/relink; one successful canonical relink followed. Within one-relink cap (B-F4).
3. **Stale snapshot files:** canonical values are from `final_verify.out`, `smoke_replay.out`, `full_replay.out` and direct recomputation (B-F3).
4. **F1 attribution limitation:** PROV alone cannot distinguish OBS edge from real aggressor; the coordinator combines it with Agent C's GDS census, which supplies the missing geometry/net evidence. No over-claim made.
5. **Sliver "artifact" wording:** confirmed artifact under the pre-registered rule, explicitly noting the box contains own-net `clk` M4 metal; this is not an "empty space" claim.

## 4. Pre-registered rule compliance

- No post-hoc threshold change; ≥90% attribution met at 100%.
- Sliver decision rule applied exactly; verdict CONFIRMED-ARTIFACT.
- Cost cap respected: one patch/relink, one smoke, one full replay, 0 debug iterations; no abort triggered.
- R2 advisory only; no activation; no scope expansion; DRT-0419 untouched.

## 5. Final adjudication

The execution is accepted. The 2 nm sliver verdict is **CONFIRMED — ARTIFACT**; DRT-0073 root cause is updated as bounded in `ENG010_SLIVER_VERDICT_AND_ROOT_CAUSE.md`. No remedy, geometry change or follow-up experiment is authorized. Await explicit approval.
