# T-ENGINEERING-015 — Independent Agent Reviews

Full reports (read-only):
- Agent A: `C:\Users\91846\AppData\Local\Temp\opencode\ENG015_A_research.md`
- Agent B: `C:\Users\91846\AppData\Local\Temp\opencode\ENG015_B_source.md`
- Agent C: `C:\Users\91846\AppData\Local\Temp\opencode\ENG015_C_assessment.md`

## Agent A — Literature and industry research

Found concrete, cited material: LEF 5.8 `OBS SPACING` and `USEMINSPACING OBS` semantics; merged PR #10856 (OBS `SPACING` honored by ODB/DRT); issue #1550 (OBS spacing model causing DRT-0073); PR #9935 (unmerged, pin-pitch-bloated OBS subtraction); merged LEF round-trip fixes #11547/#11410/#11069; merged PR #12162 (clock-pin snapper); issue #11766 (PA marker diagnosis); Cadence abstract-generation practice; TritonRoute papers. Ranked: diagnostic → OBS SPACING → USEMINSPACING OBS → generator regeneration → build check. `websearch` returned HTTP 402; GitHub API/raw docs used instead.

## Agent B — OpenROAD source research

Fingerprinted local build to upstream `a77fc27` (2026-11-04). Traced the full fail path with file:line citations. **Decisive challenge to Agent A:** PR #10856's zero-spacing early return is present locally but fires only for **abutment**; the M4 probe endpoint lies inside the OBS rectangle, so it is a true overlap and the exemption cannot apply. `USEMINSPACING OBS` / OBS `SPACING` are consulted only in the prl/abutment path. No supported config knob can create an AP when zero exist; `set_ppl_mode` absent. No upstream backport after the local commit. Ranked source interventions exist but carry physical-legality risk.

## Agent C — Independent remedy assessment

Derived the governing geometry law: broad carve wins because it leaves 1986 nm of OBS clearance; the exact-strip carve leaves only 12 nm, below 24 nm spacing and 25 nm ENDOFLINE — quantitatively explaining R1-N-W's failure. Extended west carve to x≤3461 (y held at 72 nm) is arithmetically plausible but the region is GDS-uncensused and all-pin behavior unknown. Under a strict standard, **no implementable fix is credible today**; posture = no remedy / further diagnostic.

## Reconciliation

Agent A's top two candidates were **refuted by Agent B's source evidence** (wrong predicate), not merely by prior experiments. Agent C's quantitative mechanism explains why all narrow carves failed and why broad carve succeeded, and concurs with Agent B that no currently implementable candidate is credible. The coordinator independently closed the generator avenue by reading the local generator: OBS is a hard-coded full-body blanket with no pin-aware configurability. All three reviewers converge on NO-GO for Phase 3.
