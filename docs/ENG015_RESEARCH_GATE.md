# T-ENGINEERING-015 — Phase 2 Research Gate Decision

- **Date:** 2026-11-24
- **Decision:** **NO-GO. No credible research-supported candidate survives review. Phase 3 (isolated validation) and Phase 4 (fix application) are NOT authorized.**
- **Gate owner:** coordinator, after independent review by Agents A/B/C.

## 1. Candidates evaluated and why they fail

1. **LEF OBS `SPACING 0` / `USEMINSPACING OBS ON`** (Agent A's top findings) — source inspection (Agent B) proves these affect only `checkMetalSpacing_prl_getReqSpcVal` and the abutment branch of `checkMetalSpacing_short_obs` (`FlexGC_main.cpp:657-666`). Our west probe endpoint (abs x4716) lies **inside** the OBS rect (4704–4764): this is a true overlap/short, not abutment. The documented fixes target the wrong predicate. **REJECTED.**
2. **Upstream backport** — local build ≈ `a77fc27` (2026-11-04); no later upstream fix to `FlexPA_acc_point.cpp` / `FlexGC_main.cpp` exists beyond a directory rename. Open issues #12199/#12200 have no linked fix. **REJECTED.**
3. **Clock-pin snapper fix (PR #12162)** — measurement shows `u_sram/clk` centre is exactly on M4 track #345 (0 offset). **REJECTED as inapplicable.**
4. **All prior SattvaRoute levers** — broad/narrow hand carves, R1-N, R1-N-W, C1, C2, via-in-pin, placement, pin geometry, config thresholds: already executed/refuted. **REJECTED.**
5. **Extended west carve (x≤3461, y window 72 nm)** — clears the 12 nm new-edge gap arithmetically, but the region local x3445–3474 has **no GDS foreign-net census**, no all-pin AP evidence, and a documented new-OBS-edge artifact precedent. **CONDITIONAL hypothesis, not a credible candidate.**
6. **Generator-level OBS regeneration** — the local generator hard-codes a full-body M1–M5 OBS (`lef_extractor.cpp:285-292`, `gds2lef.py:137-142`) with no pin-aware configuration; PR #9935 is unmerged; no legal corridor has been proved. **CONDITIONAL hypothesis, not a credible candidate.**
7. **Tool-source marker filtering** — would bypass the decisive predicate, but accepts AP stubs over macro metal with uncertain legality and no upstream precedent. Fails the strict physical-legality gate. **REJECTED.**

## 2. Gate outcome

- **Candidate remedy:** NONE.
- **Mechanism / supporting evidence:** documented research findings are recorded in `ENG015_RESEARCH_REPORT.md`; none applies to the confirmed true-overlap Short.
- **Why prior experiments do not disprove the rejected candidates:** a prior negative result is not the reason they are rejected — they are rejected because source semantics show they cannot affect the failing predicate, or because physical legality is unproven.
- **Predicted measurable outcome:** not applicable; no candidate to test.
- **Risks / side effects:** not applicable.
- **Preregistered test plan:** **NOT PUBLISHED — no candidate qualified.** Per the task's stop condition ("If no credible candidate survives review, stop and report research findings. Do not invent a remedy to continue"), no experiment design, scratch geometry, or source patch has been created.

## 3. Authoritative research conclusion

The exact remaining gap is now understood: the SRAM abstract intentionally models a full-body M1–M5 OBS and relies on pin shapes remaining usable where they overlap it (`lef_extractor.cpp:285-288`), while OpenROAD's pin-access DRC treats a stub overlapping that OBS outside the pin rectangle as a `Short`. The tool provides no supported semantic lever to reconcile this for a true overlap, and the upstream abutment exemption does not apply.

Resolving this would require either (a) a physically proven, pin-local OBS corridor regeneration for all macro pins, or (b) a narrowly scoped tool-source change with demonstrated routing/DRC safety. Both are separate, authorized efforts with prerequisites that are currently UNKNOWN. No such effort is authorized by this milestone.

## 4. Stop

End at this gate. No Phase 3 execution, no source/geometry/config change, no production fix, no deployment. Explicit authorization is required for any future work.
