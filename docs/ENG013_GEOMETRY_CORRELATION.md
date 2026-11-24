# T-ENGINEERING-013 — Geometry Correlation Evidence

| Item | Value | Source |
|---|---|---|
| clk pin (abs) | `(4764,16560)-(4848,16584)` | LEF:33 + origin (1230,8184) VERIFIED |
| M4 pitch | 48 nm | tech LEF VERIFIED |
| W probe endpoint | x=4716, y=16572 | pinned block-pin endpoint arithmetic VERIFIED |
| measured blocker rect | `(4704,16560)-(4764,16584)` | new PROV rect field VERIFIED |
| master OBS west strip | local x 3474–3534 → abs 4704–4764 | ODB full M4 RECT VERIFIED |
| broad carve | removes interior incl. x4704–4764 at y16572 | broad ODB dump VERIFIED |
| broad result | W clean, 3 APs accepted | replay VERIFIED |
| E-side survivor | `(4880,16560)-(4902,16584)` | broad OBS right strip VERIFIED |

The measured blocker rect matches the master OBS west strip exactly and disappears in the broad-carve DB, where W becomes clean. This is independent of the instance-level `u_sram` label (whose numeric id is unstable across runs).
