# Verification boundaries

Status: authoritative boundary statement. Related: `docs/architecture/VERIFICATION.md`, `docs/product/NON_GOALS.md`, `docs/research/LIMITATIONS.md`.

## What a verified PASS means

A `verify_run.py` PASS means: declared stages executed, endpoint artifacts are present and non-empty, selected report signals satisfy the tool-level checks, and evidence is complete enough to support those specific claims. It is a **report-level** verdict for the pinned control benchmark.

## What a verified PASS does not mean

- **Not signoff.** No foundry DRC/LVS, no antenna/power/IR-drop/antenna/EM signoff, no SDF or formal functional signoff.
- **Not foundry DRC.** Router or OpenROAD-internal `DRT-0199 = 0` and `5_route_drc.rpt` are tool-level, not foundry rule decks.
- **Not timing closure.** Single typical corner with a trivial 1 ns constraint is not characterized multi-corner timing closure.
- **Not coverage.** Scan/stuck-at coverage is not established by PnR completion.
- **Not functional correctness.** Timing cleanliness says nothing about logical function.
- **Not engineering acceptance.** A human must interpret reports for the design's goals.

## Boundary chain

```
tool exit code (rc=0)
  ≠ flow completion (all stages in this run)
    ≠ engineering report signals clean
      ≠ timing closure / coverage
        ≠ characterized timing
          ≠ foundry signoff
```

Each arrow requires additional evidence. SattvaRoute implements checks for the early links in that chain and explicitly labels the later ones as not evaluated.

## Honest status usage

Use `NOT EVALUATED` / `UNKNOWN` / `INCONCLUSIVE` when a boundary is crossed without evidence. Do not write "PASS" for signoff, functional correctness, or multi-corner timing.

## Related

`docs/reference/STATUS_CODES.md`, `docs/engineering/SDC_TIMING.md`, `docs/engineering/PLACE_ROUTE_EXTRACTION.md`.
