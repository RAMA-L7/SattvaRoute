# T-ENGINEERING-014 — Coordinator Adjudication

## 1. Reconciliation of the three reviews

| Reviewer | Core verdict | Adjudication |
|---|---|---|
| A — Remedy feasibility | VIABLE: class 6; CONDITIONAL: classes 1 & 5; NOT VIABLE: classes 2/3/4 | **ADOPTED** with the correction that rect/fixed enrichment is already executed (ENG013-B); the residual diagnostic gap is object class/owner/net |
| B — Independent physical review | Broad carve proves mechanism not legality; west strip contains own-net `clk` metal; every legal narrow carve fails; ~120 nm EOL envelope cannot fit at 96 nm pitch | **ADOPTED** — materially strengthens the case against treating any carve as a remedy |
| C — Validity / reproducibility | Broad carve is a reproducible bounded positive control; everything beyond it (production remedy, routing/DRC, timing, all-pin AP, physical legality, minimality) is INFERRED/UNKNOWN; recommends a future bounded minimal-strip experiment conditional on approval | **ADOPTED IN PART** — findings and provenance caveats adopted; the "run the bounded experiment now" recommendation is **REJECTED as premature** (see §3) |

## 2. Points of agreement (uncontested)

1. The blocker is a fixed M4 master-OBS strip, geometrically and by `fixed=1`; instance labels are non-authoritative. (VERIFIED)
2. Broad carve is a diagnostic counterfactual that establishes **causality at `pin_access` only**; it is not authorization, not a production solution, and not evidence of route/DRC/timing/all-pin health. (VERIFIED)
3. No remedy was executed; no geometry, LEF/GDS/ODB/DEF, source, config, or production artifact was changed in this milestone. (VERIFIED)
4. All prior approvals (D-022, D-023) are consumed and non-transferable; any implementation requires a new decision ID and explicit approval. (VERIFIED)

## 3. Claims explicitly rejected as unsupported

- "Broad-carve 3-AP success proves a production remedy exists." **REJECTED** — frees 120 `M4/0` + 92 `M4/251` real shapes including foreign nets.
- "The exact blocker rectangle identifies the aggressor object class, so carving it is safe." **REJECTED** — `(layer, rect, fixed)` is decisive geometrically; object type/net was never emitted; the strip contains own-net `clk` metal and R1-N-W already freed it with 0 APs.
- "A minimal west-strip carve will pass whole `pin_access` / routing." **REJECTED** — no all-pin evidence; `clk`→`ce_n` failure transfer precedent; no route/DRC/timing run.
- "Config flags or placement changes can create the first AP." **REFUTED** — tested no-op / directly refuted.

## 3b. C-vs-B conflict resolution

Agent C argues that the minimal west-strip carve is the "smallest untested mechanism-specific geometry" and recommends a bounded experiment. **The coordinator rejects this premise.** Agent B's verified record shows FDE-007 R1-N-W carved corridor x=3474–3672 with y±24 — which **includes the exact west strip** `(3474,8376)-(3534,8400)` — and still produced 0 accepted APs. The blocker rect being the *binding* constraint at the first candidates does not mean removing it is *sufficient*; after removal, other marker families (spacing/EOL/via) become binding (B §1.3; ENG011 C1/C2). Agent C's "positive control exists" argument is accepted only in the bounded sense: broad carve is a reproducible `pin_access` counterfactual, not evidence of a physically legal or sufficient remedy.

Agent B's strongest objection (INFERRED, high confidence) is therefore adopted as the governing risk: the only geometry that demonstrably yields APs is physically illegal, and every physically legal narrow carve tested to date fails `pin_access` because the ~120 nm EOL/corner envelope cannot fit at 96 nm pin pitch (adjacent-net metal 24 nm away < 25 nm ENDOFLINE). No quantitative proof that a legal geometry exists has been produced.

## 4. Adjudicated decision

**No remedy is authorized. The evidence does not support a bounded remedy experiment now; it supports further diagnostic work first.** Under current constraints there is **no demonstrated viable remedy**: the only geometry yielding APs is physically illegal, and every physically legal narrow carve tested (R1-N, R1-N-W, C1, C2) produced 0 APs. This is not a claim that no remedy can ever exist — that would overstate the negative (Agent C's valid caveat) — but no legal, sufficient geometry has been demonstrated.

The only defensible immediate posture is **no remedy + further diagnostic** (class 6), where the required diagnostics are the prerequisites C itself enumerated: full-strip GDS census, all-pin AP survey, marker object-type/net provenance, quantitative rule-envelope proof, canonical no-op-controlled DB diff, and a written full-flow plan. Two conditional paths are recorded for a *future, separately authorized* milestone:

1. **Class 1 (minimal west-strip carve)** — CONDITIONAL: the narrowest causal descendant of the broad carve, but its x-extent was already freed in R1-N-W and failed; it is **not** authorized as an experiment until the rule-envelope proof and C's prerequisites are satisfied. Not a production fix by itself.
2. **Class 5 (generator-level OBS semantic regeneration)** — CONDITIONAL last resort: a principled all-pin path but wholly unevidenced (configurability, defect status, effect on M4 OBS) and largest-scope.

Classes 2/3/4 are rejected.

## 5. Evidence boundary

Every conclusion above derives from published ENG009–ENG013 artifacts and the three read-only reviews. Nothing in this milestone established new physical measurements or executed any flow. Literal tech-LEF rule text for `rid=48`, aggressor object class/net, full-strip GDS vacancy, all-pin AP status, and full-flow signoff remain explicitly UNKNOWN.

## 6. Stop

Publication of T-ENGINEERING-014 closes this milestone. No subsequent milestone, remedy, experiment, or implementation without explicit user authorization.
