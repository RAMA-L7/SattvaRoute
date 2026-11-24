# T-ENGINEERING-015 — Evidence-Driven Research and Gate: Final Report

- **Date:** 2026-11-24
- **Status:** COMPLETE at Phase 2 research gate. **NO-GO. Stop.**
- **Decision:** No credible research-supported remedy candidate survives review. No experiment, source change, geometry change, or production change was made.

## 1. What was accomplished

Three independent research workstreams were commissioned under read-only ownership:
- **Agent A** searched authoritative docs, GitHub issues/PRs, industry material, and TritonRoute papers, finding concrete OBS-spacing and upstream-fix candidates with citations.
- **Agent B** traced the exact OpenROAD source path with file:line evidence and **refuted A's top candidates** at source level.
- **Agent C** independently derived the quantitative geometry law explaining why broad carve works and every narrow carve fails.
- **Coordinator** closed the generator avenue by direct inspection of the local macro generator.

No EDA flow was run; no shared file was concurrently edited; no protected artifact changed.

## 2. Authoritative research findings

1. The failure is a **true overlap Short** against the target macro's own fixed M4 OBS, not an abutment or prl-spacing failure. The west probe endpoint (abs 4716) lies inside the OBS rect (4704–4764).
2. The documented upstream abutment exemption (PR #10856, code present in this build) and `USEMINSPACING OBS` / OBS `SPACING` semantics affect only the prl/abutment path — they cannot suppress this Short.
3. No supported `pin_access` Tcl/config knob can create an AP where zero exist; `set_ppl_mode` is absent; the clock pin is already exactly on-track, so PR #12162 does not apply.
4. No later upstream fix exists in the relevant code area; open issues #12199/#12200 have no linked fix.
5. Narrow carves fail because removing the blocker leaves a new OBS edge only 12 nm from the probe endpoint (24/25 nm limits). Broad carve succeeds because it leaves 1986 nm clearance — but it is physically illegal.
6. The macro abstract generator emits a **hard-coded full-body M1–M5 OBS** with no pin-aware configurability; regenerating a legal pin-local abstract would require a generator source change plus proofs that do not exist.
7. Tool-source marker filtering could bypass the predicate but fails the physical-legality gate (could admit AP stubs over real macro metal; no upstream precedent).

## 3. Gate decision

**NO-GO.** See `ENG015_RESEARCH_GATE.md`: no candidate, no mechanism to test, no preregistered plan invented. Stop conditions triggered: no credible research-supported candidate; physical-design legality of the remaining hypotheses uncertain.

## 4. Deliverables

`ENG015_BASELINE_RECORD.md`, `ENG015_RESEARCH_REPORT.md`, `ENG015_CANDIDATE_COMPARISON.md`, `ENG015_RESEARCH_GATE.md`, `ENG015_INDEPENDENT_REVIEWS.md`, `ENG015_COORDINATOR_ADJUDICATION.md`, this report, plus updated `REPORT_INDEX.md`, `PROJECT_STATE.md`, task board, logs, handoff. No scratch experiment results and no validated fix exist because no candidate was authorized.

## 5. Integrity

KB verify PASS (19/19), protected artifacts 9/9, validator 13/13; publication tree clean and HEAD equals remote. R2 advisory/inactive. Historical milestones preserved.

**Stop at this milestone. No additional remedy iteration, implementation, or production deployment without explicit user authorization.**
