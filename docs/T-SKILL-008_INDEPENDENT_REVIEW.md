# T-SKILL-008 — Independent Review (Agent B, blind)

- **Reviewer:** Agent B, independent of Agent A; did not read `T8_A_*`.
- **Target:** P-SHADOW-002 (`185ecee2…`), R2 (`6900ebc8…`), design/shadow stage.
- **Verdict:** **NO EXECUTION AND NO APPROVAL RECOMMENDED** in the proposal's current form.

## 1. Independent validity conclusions

P-SHADOW-002 is an honest shadow-stage artifact and a legitimate `causal diagnostic`, but it is not
gate-ready. Three issues are disqualifying at a real gate:

1. **A17 measurement capability (UNKNOWN → STOP).** The bar requires exact pin-center coordinates, M3
   offsets and DRT-0419 bboxes, but FDE-004 §5 records no candidate-level coordinates and D-016 records
   aggregate-only tool output. If only aggregates exist, the causal question is untestable at the
   proposed resolution. A17 cannot be DEFERRED — R2-J makes UNKNOWN a STOP for dependent items.
2. **A4 single-variable isolation (UNKNOWN/PARTIAL).** `place_macro -exact` is macro-level (FDE-004 §6);
   "only D/Q target coordinates adjusted" is incoherent. The plausible implementation shifts the whole
   macro, moving all 22 pins and perturbing `clk` geometry/OBS — a confound with the DRT-0073 mechanism.
   The "same ODB" statement also contradicts a placement change baked into the ODB.
3. **A3 control identity (PARTIAL/UNKNOWN).** Arm A is defined by a *historical* run while its role says
   "concurrent". R2 explicitly bars a prior historical run as a concurrent control. A fresh run with a
   modification digest equal to the approved baseline is required.

## 2. Areas where the design was sound

- Class label `causal diagnostic` correctly prevents mechanism-only N/A exemptions for A3/A4/A6 and
  correctly denies the A13 no-remedy bounded-resource exception (A/B/C agree).
- N=1 per arm with DRT-0419 markers and per-pin measurements as sub-units — no pseudoreplication.
- A6 deterministic order rule committed.
- No-remedy boundary adequate at shadow stage; must be carried verbatim into any fixed bar.
- Correct stage handling: A15 DEFERRED-SHADOW; A9/A10/A11-preflight/A12(b)/A16 legitimately DEFERRED
  with named artifacts/owners. Forcing these to FAIL in a shadow review would reproduce the J1/J2 defect
  R2 exists to fix. They are not silent PASSes.
- D-012 correctly treated as a historical decision, not a remedy family.

## 3. A7 disagreement (reconciled by coordinator)

Agent B scored A7 PARTIAL/conditional-N/A because the treatment is placement-shaped (FDE-004 §12 R3)
and KB family content could not be established from allowed files. Agent A scored N/A because no
remedy-family *value* appears. **Coordinator adjudication:** R2-H triggers on a family value named
anywhere; the proposal mentions only the schema field name `relationships.remedy_family`, not a value.
A7 = **N/A** stands, with a latent obligation to run `assess`/`duplicate_check` if any family value
(including a placement family found in the KB) is later named. Agent C's value-vs-field-name ambiguity
is recorded as an R3 clarification. CLI naming discrepancy noted (`duplicates` vs `duplicate_check`).

## 4. Real-gate blockers (priority order)

1. A17 probe results for every measurement the bar depends on; if aggregate-only, rewrite or block.
2. A4 modification digest and resolution of the macro-scope/ODB contradiction.
3. A3 fresh concurrent identity control with digest and concurrence.
4. Completion of design-stage fields A5/A8/A11/A12/A13/A14 and naming of DEFERRED artifacts/owners.

No-execution/no-approval recommendation is unconditional; this review activates nothing.
