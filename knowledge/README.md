# knowledge/ — SattvaRoute engineering memory

This directory is the append-oriented Knowledge Base ledger for the project.

- `kb_records.jsonl` — one JSON knowledge record per line. **Never edit or delete a line.**
  Corrections are appended as new records with `relationships.supersedes`.
- `kb_manifest.json` — derived counts/histograms; regenerated automatically.
- `kb_immutable_manifest.json` — SHA-256 of protected artifacts at init; used by `verify-immutable`.
- `fde_seed.json` — reviewed FDE-derived records; `seed` appends only records whose ID is absent.
- `queries/` — example failure queries for retrieval/applicability demonstration.

Full operating manual: `docs/KNOWLEDGE_BASE.md`.
Audit and integration plan: `docs/KB_AUDIT.md`.

Quick checks (WSL, from `/mnt/d/SattvaRoute`):

```bash
python3 scripts/sattva_kb.py verify --store knowledge/kb_records.jsonl --knowledge-root knowledge
python3 scripts/sattva_kb.py verify-immutable --manifest knowledge/kb_immutable_manifest.json --project-root .
python3 scripts/sattva_kb.py metrics --store knowledge/kb_records.jsonl --knowledge-root knowledge
```
