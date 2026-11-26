# Support

## What support covers

SattvaRoute is a research prototype maintained on a best-effort basis. Support is limited to: understanding documented behavior, reproducing the pinned control benchmark, interpreting diagnosis/verification output, and reporting defects with evidence.

## Before asking

1. Read `docs/DOCUMENTATION_INDEX.md` and `docs/workflow/GETTING_STARTED.md`.
2. Check `docs/workflow/TROUBLESHOOTING.md` and `docs/reference/FAQ.md`.
3. Confirm preflight passes (`python3 scripts/manifest.py --check --profile nangate_macro_control --mirror <orfs>`).
4. Run the offline suite: `python3 -m unittest discover -s tests -p 'test_*.py'`.

## Reporting a problem

Open an issue (unless it is a security or conduct concern) with:

- exact command and environment variables (redact secrets),
- run ID/tag and stage,
- verbatim log excerpt and report paths,
- tool versions/hashes,
- expected vs observed behavior,
- which evidence you inspected, and whether you checked `docs/reference/STATUS_CODES.md`.

Separate observed evidence from hypothesis. Do not claim a defect without evidence.

## Security and conduct

Report vulnerabilities privately per `SECURITY.md`; report conduct concerns privately to maintainers as described in `CODE_OF_CONDUCT.md`.

## Boundaries

No promise of response time, feature delivery, production support, or signoff assistance. Scope is the pinned `nangate_macro_control` benchmark; other PDKs/macros are not validated. See `docs/research/LIMITATIONS.md`.

## Related

`CONTRIBUTING.md`, `SECURITY.md`, `docs/reference/FAQ.md`, `docs/workflow/TROUBLESHOOTING.md`.
