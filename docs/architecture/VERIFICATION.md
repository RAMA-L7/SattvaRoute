# Verification system

Status: implemented. Source: `scripts/verify_run.py` (the Phase 5 note at `docs/VERIFICATION.md` is preserved as historical/superseded).

## Separation principle

Verification is a **separate responsibility** from diagnosis, approval, and recovery. The same component that proposes or applies a change never declares it successful. `verify_run.py` is offline and read-only with respect to the run it inspects.

## Five questions

`verify_run.py` is built around five questions a return code cannot answer:

1. **Execution** — did every declared stage run, in this run directory?
2. **Artifacts** — are endpoint products present and non-empty?
3. **Engineering** — do reports show clean routing/timing/extraction?
4. **Evidence** — is the evidence complete enough to support the claim?
5. **Recovery** — did an approved change actually fix the target failure (baseline vs failure vs recovery)?

## Endpoint products checked

`5_route.odb`, `route.guide`, `6_final.odb`, `6_final.spef`, `6_final.def`, `6_final.gds`, `6_final.v`, `6_final.sdc`; reports `6_finish.rpt`, `5_route_drc.rpt`.

## Report signals

- Routing: last `[INFO DRT-0199] Number of violations = N` in the stage log (intermediate counts are explicitly not used).
- Extraction: `[INFO RCX-0045] Extract N nets`; unannotated driver counts.
- Timing: period/fmax, worst slack, setup/hold violation counts, TNS/WNS — interpreted in the units established by `report_units`/Liberty.
- Empty report is clean only when the tool log shows completion with a zero violation count.

## Status aggregation

Checks return `PASS`, `FAIL`, `UNKNOWN`, `NOT_EVALUATED`. Aggregation rules: any `FAIL` → fail; else any `UNKNOWN` → unknown; all `PASS` → pass. Missing evidence is never a pass. Two identically incomplete runs both fail.

## Recovery comparison

`--baseline B --failure F --recovery R --audit-map ... --approval-apply ...` compares per-check statuses and flags any recovery `FAIL` where the baseline was `PASS` as a regression. View helpers construct audits per run directory.

## Usage (verified against argparse)

```
python3 scripts/verify_run.py --run <run> [--audit <audit.json>]
python3 scripts/verify_run.py --baseline B --failure F --recovery R --audit-map <audits.json> --approval-apply <A.json>
```

Optional flags: `--targeted-marker`, `--out`.

## What verification does not claim

- Not foundry DRC/LVS/signoff. Router DRC=0 ≠ foundry DRC.
- Not functional correctness; timing results do not prove function.
- Not timing closure at characterized multi-corner signoff.
- Not "flow completed = engineering accepted". Engineering validation remains human.

## Related

`docs/reference/STATUS_CODES.md`, `docs/engineering/VERIFICATION_BOUNDARIES.md`, `docs/architecture/RECOVERY.md`.
