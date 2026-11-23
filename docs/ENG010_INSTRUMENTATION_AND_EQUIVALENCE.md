# T-ENGINEERING-010 — Instrumentation and Equivalence Evidence

- **Experiment:** ENG009-DIAG-001-20261124T000000Z-0001
- **Approval:** ENG010-AP-001 (`experiments/.../evidence/APPROVAL.md`)
- **Status:** executed within approved scope; no abort condition triggered.

## 1. Patch and binary provenance

| Artifact | SHA-256 |
|---|---|
| Proposal | `18cb9017b94eb383fe552b8bac49839e391113c791a62b38a86656bb8362ff8f` |
| Source pre-patch | `0fc94a9d349604e7cc96ea09c04caa5b78a26f7c90a6a82910d5dca6fb7c0c04` |
| Source post-patch | `0815de7db1bd171609f6fcefb645608b4bbbbf617401aa6980a8d1dc74dc1299` |
| Provenance diff | `92ef2aac57dfced58fec3ab66810be4866aa8041d27450c804fc036c78f86147` |
| Original instrumented binary (preserved) | `0d890431065688930e8b140cb644e304a0a3a6beeaf32b2cff762a8aa000d33d` |
| New relinked binary | `7461d0d001768831a47095e60c17ee6a0cf34ce2890bfd5534e23f17b7e51841` |
| Production binary (unchanged) | `c1b90e0af69bc9779cde8fd1579a92a10738ddebb9ea16e459f280556c349ee9` |
| Frozen ODB (unchanged) | `35bff121b42b070023f7b9704ab2c8bd1d5dbb0027f403fde7dd8eb8161400e1` |
| Full provenance log | `92b2a54e622be2ae2ccb5ee2442c1a12d12ce24c81275ca2dcdc0c29be0c7825` |

Patch: 66 log-only additions (plus diff headers), 0 removals; no DRC, control-flow, threshold, candidate-data or debug-gate change. `patch --dry-run` RC=0.

## 2. Build execution

- Detached bazel client was SIGKILLed (RC=137) after stalling **before any compile/relink**; binary unchanged. A supervisor then ran the identical canonical recipe on the identical patched tree, RC=0, producing the new binary. This is one successful relink, within the approved cost cap (F4).
- No production source/binary or baseline was modified. The relink overwrote the in-place native build output; the original binary was preserved from a hash-verified scratch copy before relink (F2/F4).

## 3. Equivalence (recomputed independently)

| Comparison | Result |
|---|---|
| Original binary debug-OFF vs new binary debug-OFF, paths normalized | **byte-identical**, 0-line diff (normalized SHA `917014AB…`) |
| New debug-OFF vs debug-ON | only 2 pre-existing `[DEBUG DRT-pin_access]` lines + expected Tcl line-number shift (5→6); after removing those artifacts, identical |
| All three arms RC | 1, from the same pre-existing `DRT-0073` |
| Census | original OFF 0 FDE006R; new OFF 0; new ON 346 FDE006R = **107 MARKER + 107 PROV** + 132 other; 27 planar + 80 via |

**Instrumentation neutrality demonstrated.** Marker generation behavior did not change.

## 4. Agent B independent audit findings

Verdict **ACCEPT WITH LIMITATIONS**:
- Patch PASS: pure additions, null-safe/const-correct label helpers, 107/107 MARKER↔PROV pairing, 0 mismatches.
- Build PASS: hashes and RC verified; protected artifacts unchanged.
- Equivalence PASS: recomputed from primary logs, not Agent A's summary.
- Non-blocking F1: PROV lines give object identity but not aggressor rect/net and do not label OBS explicitly; attribution must be combined with Agent C's GDS census. F2–F4: authorship wording, stale snapshot files, and RC=137 accounting — all documented, none blocking.
