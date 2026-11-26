# Licensing

Status: license audit and recommendation only. **LICENSE was not changed.** See `docs/governance/THIRD_PARTY.md` for the full attribution inventory.

## Project license

`LICENSE`: MIT, `Copyright (c) 2026 SattvaRoute contributors`. It explicitly applies **only to original SattvaRoute code and documentation** in this repository and not to third-party tools, PDKs, libraries, or collateral.

## What is covered

Original scripts under `scripts/`, documentation under `docs/` and root Markdown, configuration/policy files authored for this project, and curated evidence authored by the project.

## What is not covered

ORFS, OpenROAD, Yosys, Nangate45 platform data, `fakeram45_64x32` views, ASAP7 academic PDK, OpenFinRAM-generated macro collateral, and any external tool binary. These remain under their own upstream terms and are **not vendored**.

## Redistribution posture

- The repository publishes source/docs/config/curated summaries only.
- Large run databases (`*.odb`, `*.gds`, `*.spef`, full `runs/`/`work/`) are excluded.
- Platform LEF/Liberty/RCX files are referenced by hash via the manifest, not committed.
- The published `nangate_macro_control` package contains project-owned design files and provenance; external platform data must be acquired by the reader under its own terms.

## Recommendation (owner decision required; not applied)

1. Keep MIT for original SattvaRoute code/docs — it is consistent with the research-prototype posture and the existing notice.
2. Before redistributing any derived platform/macro bundle, verify the Nangate45 platform and `fakeram45_64x32` terms with the upstream licensor; the ORFS script license does not automatically cover all platform data.
3. Add explicit per-file notices to any future third-party asset included in the repository.
4. Do not claim that public availability implies redistribution rights.

No legal conclusions are made beyond the available license text. Changing `LICENSE` requires explicit owner approval and is out of scope for this milestone.

## Related

`LICENSE`, `THIRD_PARTY_NOTICES.md`, `docs/governance/THIRD_PARTY.md`, `docs/REPRODUCIBILITY.md`.
