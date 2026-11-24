# T-ENGINEERING-013 — Instrumentation Neutrality

- Source before `0815de7d…`, after `797b282c…`; patch diff `8495405b…`; binary before `7461d0d0…`, after `db876fbf…`.
- Patch scope: `fde006rPairsLabel` string formatting only — adds `rect=(xMin,yMin,xMax,yMax) fixed=<0|1>` to victim/aggressor labels. No DRC, control-flow, threshold, candidate, geometry or debug-gate change; dry-run and apply checks passed.
- Debug-off new binary vs ENG011 control log: no patch-attributable difference (only a pre-existing aggregate sparse line differs).
- Debug-on old vs new: 107/107 changed lines are PROV lines gaining rect/fixed; 0 non-PROV changes; DRT-0073=2, DRT-0305=0, marker/candidate counts identical.
- Build: one incremental relink, detached, RC=0. Replays: control RC=1, broad RC=0; no abort condition; protected hashes unchanged.

Conclusion: instrumentation is behavior-neutral; observed W blocker is geometric, not a logging artifact.
