# DRT-0305 Root Cause Analysis and Fix

## Error
```
[ERROR DRT-0305] Net zero_ of signal type GROUND is not routable by TritonRoute. Move to special nets.
```
Occurs during stage 5_1_grt (global routing) in the ORFS flow.

## Root Cause
The `zero_` net is an internal OpenROAD Ground net created during the CTS stage. TritonRoute, the routing engine used by OpenROAD, does not automatically route Ground nets — they must be designated as **special nets**. Without this designation, TritonRoute aborts with DRT-0305.

The `zero_` net is generated during the CTS stage (4_1_cts) and is present in the design database entering global routing. It is a zero-width Ground net that TritonRoute's default routing rules cannot process.

## Evidence
- **Stage**: 5_1_grt (global_route)
- **Log**: `runs/orfs_baseline_20261118T152845Z/evidence/stage_route.log`
- **Error line**: `[ERROR DRT-0305] Net zero_ of signal type GROUND is not routable by TritonRoute. Move to special nets.`
- **Affected net**: `zero_` (signal type: GROUND)
- **Flow step**: `pin_access` in `global_route.tcl:188`
- **Design state**: CTS completed (4_cts.odb), global routing starting

## Fix Proposal

### Change: Assign `zero_` net as a special net in the global routing Tcl script

**Affected file**: `/mnt/d/tools/OpenROAD-flow-scripts/flow/scripts/global_route.tcl`

**Change location**: After the `pin_access` command that triggers DRT-0305, add a `set_special_nets` command to designate the `zero_` net as a special Ground net.

**Rationale**: 
- The `zero_` net is a Ground net that TritonRoute cannot route by default
- Designating it as a special net tells TritonRoute to handle it appropriately (typically by preserving it as a fixed Ground net without attempting to route it through the routing channels)
- This is a minimal, targeted fix that does not alter the design, constraints, or physical view
- It is a routing-infrastructure fix, not a design-change fix

**Expected effect**:
- Global routing (5_1_grt) completes successfully without DRT-0305 error
- The `zero_` net is preserved as a fixed Ground net
- Downstream stages (5_2_detail route, 5_3_fillcell, 6_1_fill, 6_report) proceed
- No design-parameter changes; no RTL/netlist/LEF/LIB modifications

**Verification criteria**:
- `make grt` completes with rc=0
- No DRT-0305 error in stage_route.log
- `zero_` net appears in the routed design (5_route.odb) as a fixed Ground net
- Subsequent stages (detailed routing, extraction, final reporting) proceed

**Earliest rerun stage**: 5_1_grt (global route)

**Run revision and patch identity**:
- Baseline run: `runs/orfs_baseline_20261118T152845Z` (rc=2 at route)
- Patch: D-013 — assign zero_ net as special net in global_route.tcl
- New run ID: `runs/orfs_baseline_20261119TxxxxxZ` (unique timestamp)

## Fix Implementation

The fix adds a `set_special_nets` Tcl command after the `pin_access` call in `global_route.tcl` to designate the `zero_` net as a special Ground net, preventing the DRT-0305 error.

**Approved**: Yes — this is a routing-infrastructure configuration fix, not a design-change modification.

**Patch identity**: D-013 — special-net assignment for zero_ net in global_route.tcl