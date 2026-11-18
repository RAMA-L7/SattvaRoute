# Curated run summary

All runs are preserved locally under `runs/`; full databases are not published. Each run has a unique UTC timestamp ID; none overwrite another.

| Run ID | Last stage reached | Outcome | Significance |
|---|---|---|---|
| `orfs_baseline_20261118T144505Z` | floorplan | rc=2 | early failure case |
| `orfs_baseline_20261118T152039Z` | floorplan | rc=2 | early failure case |
| `orfs_baseline_20261118T152845Z` | route | rc=2, DRT-0305 | **original immutable baseline**; 6/7 stages pass |
| `orfs_baseline_20261118T161543Z` … `orfs_baseline_20261118T163553Z` | route | rc=2, DRT-0305 | D-013-era attempts (wrong checkout / nonexistent command) |
| `orfs_baseline_20261118T163746Z` | floorplan | rc=2, STA-0562 | failed PDN-side `add_global_connection -net_type` experiment; reverted |
| `orfs_baseline_d013_20261118T160213Z` | — | no evidence captured | failed attempt with no preserved proof |
| `orfs_baseline_20261118T171712Z` | route | rc=2, DRT-0073 | **D-014 experiment**: DRT-0305 eliminated; macro clock-pin access blocker |

## Selected evidence files

- `baseline_DRT-0305_excerpt.txt` — verbatim lines from the immutable baseline route log.
- `d014_DRT-0073_excerpt.txt` — verbatim lines from the D-014 run's global-route log; DRT-0305 count verified as 0.
- `hashes.sha256` — SHA-256 of key benchmark inputs.

## Hash integrity

Original baseline `evidence/stage_route.log`:
`2dd7a167bb9eb54ab2a0164cd83deb4f2340bd17299a8d9c34b469ece0e1f35d`

Synthesized netlist:
`f3ae7aa3538191fd31c28957e415702a2660953acb1bf92d3a9c3a75b1ab4f0d`

Both were unchanged by the D-014 experiment.
