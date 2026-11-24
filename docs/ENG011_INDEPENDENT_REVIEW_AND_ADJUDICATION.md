# T-ENGINEERING-011 — Independent Review and Coordinator Adjudication

## 1. Agent verdicts

| Agent | Verdict | Key result |
|---|---|---|
| A — geometry/rules | analysis complete | 120 nm y envelope derived; injection technically available; prior governance STOP noted but superseded by ENG011-AP-001 |
| B — candidate design | analysis complete | C1/C2/C3 candidate RECT blocks; C3 later rejected |
| C — independent physical review | **ACCEPT WITH LIMITATIONS** before execution; **results review** after execution | control confound fixed; C3 rejected; y-hypothesis refuted by results |

## 2. Pre-execution findings resolved

- **Comparator confound:** raw source ODB replaced by a **no-op rebuilt ODB** using the same DEF pipeline; `r1n_ref` path-matched. Agent C confirmed this isolates y-only for C1.
- **C3 rejected:** it was R1-N Variant B and re-blocked VIA34/VIA45 pads; not executed.
- **C1 ambiguity:** 48 nm perpendicular mapping remains INFERRED, but a maximal legal diagnostic is valid because the tool's aggressor is the OBS object; no production claim made.
- **C2 risk:** x=3618 seam predicted to add spacing markers — confirmed (Metal Spacing 63→121).

## 3. Post-execution adjudication

- C1 produced the same marker type census as r1n_ref and 0 APs → y-envelope remedy hypothesis **REFUTED**.
- Marker bboxes shifted exactly to the new OBS edges → confirms OBS object as aggressor; not foreign metal.
- Control and path-matched reference used the same rebuilt-DB path → no injection confound.
- C2 actively harmful; reject.
- Ranking: **no-remedy** (best supported) > C1 = r1n_ref (no gain) > C2 (harmful).

## 4. Governance

ENG011-AP-001 explicitly authorizes this bounded diagnostic; prior D-022/D-023 STOP conditions are not bypassed because no production remedy is applied and no geometry is promoted. R2 advisory only; no activation. No historical report or KB record rewritten.

## 5. Final disposition

Accept the evidence; close the y-envelope remedy hypothesis family. No candidate proceeds to production. Await explicit authorization for any follow-up experiment or remedy.
