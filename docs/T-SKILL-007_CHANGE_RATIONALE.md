# T-SKILL-007 — R2 Change Rationale (defect → disposition)

- **R2 scored hash:** `f81618a9a977c33deb938465178170da7cedeb9b904cfb6fe391ff0fd4863b31`
- **R2 final hash:** `6900ebc8b17821f7b1bb30f29224d0eb120042fd5e392dbbf42046877ba4cb9d`
  (citation-only correction F1; no scoring or operative text changed)
- **Preserved snapshots:** R0 `a445c7ae…e0c091`, R1 `286c7bbaa…1fc4f` — both byte-for-byte unchanged.

## 1. Verified defects and dispositions

| Defect (source) | R2 revision | Operative disposition |
|---|---|---|
| J1 — execution/post-run artifacts demanded at `design` (T6_C §3) | R2-A Stage column + DEFERRED | `design`/`execution`/`post-run` stages declared per item; at `design`, execution/post-run evidence is **DEFERRED** with named artifact + owner; DEFERRED is neither PASS nor NO and does not trigger STOP |
| J2 — A15 forced NO on shadow input with no approval gate | R2-E | `DEFERRED-SHADOW` disposition; absent sign-off is not NO when no approval exists; scope unified to A1–A17 |
| J3 — multi-arm non-causal diagnostic fits no class | R2-K | four classes: `mechanism-only diagnostic` / `causal diagnostic` / `remedy validation` / `baseline`; A3/A4/A6 N/A for mechanism-only with no-contrast claim recorded |
| J4 — "instrumentation identity" naming trap can yield false A3 PASS | R2-F | only a **modification-digest identity** qualifies; instrumentation-neutrality arms are never controls |
| J5 — fabricated cost cap on no-remedy scope | R2-D | bounded-resource statement required; "one further iteration authoriser" sub-check N/A for no-remedy scope |
| J6 — family named as non-goal skips KB check | R2-H | any family key appearing (even as non-goal) requires verbatim key + `assess`/`duplicate_check` |
| J7 — stale §B "A1–A12" reviewer reference | R2-E | all references unified to A1–A17 |
| J8 — reviewer double-counting across A9/A15 | R2-L | single merged §B reviewer row referenced by both |
| M1 — `getSrcs()` availability not verified (load-bearing) | R2-B + **new A17** | A17 mandatory measurement-capability preflight: API/tool name, version, build SHA, read-only probe result, §B evidence-field producibility; UNKNOWN on required capability = STOP for dependent item |
| M2 — GDS tooling/version + layer/datatype map unrecorded | R2-I | KLayout/Python version + mapping table appended to A14 and §B |
| M3 — detached-build contingency absent | R2-B | execution mode, heartbeat/owner and STOP rule for builds with documented blockage history |
| M4 — explicit no-remedy boundary absent | R2-K | every class records no-remedy/no-production-change boundary; evidence implying a remedy → STOP + new proposal |
| M5 — per-marker provenance / net classification / out-of-scope record missing | R2-J + §B additions | required evidence fields added to §B |
| M6 — KB family check under-triggering | R2-H | see J6 |
| T-004: A3 self-contradiction, A7 wrong key/term, A8 remedy bar on diagnostics, A12 `tools/` false positive, A6 over-strict order, A10 bare N/A, A13–A15 omissions, A16 demotion, ED-1/ED-2 | carried forward | all retained and sharpened in R2 §F.2(c); no regression found by Agent B |

## 2. Structural changes

1. **Stage column** added to the A-table and §A.1; GATE RULE is stage-aware.
2. **Sixth disposition** `DEFERRED` (plus named `DEFERRED-SHADOW` for A15) alongside
   PASS / FAIL / PARTIAL / UNKNOWN / N/A.
3. **A17** added as a mandatory item; A1–A17 all individually testable.
4. **Four-class applicability model** replacing the three-class model.
5. **Explicit lineage table** (R0 → R1 → R2) and revision ledger retained in R2 §F.

## 3. Non-changes

R2 is DRAFT/INACTIVE; not installed, not active, not a gate. No EDA, experiment, activation,
installation, remedy, production, KB, approval, historical FDE report or protected artifact changed.
No preventive-effectiveness claim is made.
