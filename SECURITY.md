# Security policy

## Reporting vulnerabilities

Please report security issues privately through GitHub's "Report a vulnerability" feature for this repository, or by contacting a maintainer directly. Do not open a public issue for an unfixed credential exposure or vulnerability.

Include: affected file/path, impact, reproduction steps, and suggested remediation. Please allow time for a fix before public disclosure.

## Preventing credential disclosure

- Never commit API keys, tokens, passwords, SSH keys, `.env` files, or cloud credentials.
- Use environment variables for secrets; keep local configuration out of the repository.
- Before pushing, scan staged files for `gho_`, `ghp_`, private-key headers, and personal absolute paths.
- `.gitignore` excludes common secret filenames, but it is not a substitute for reviewing `git diff --cached`.

## Scope

This is a research prototype. It does not implement an authentication service, a network daemon, or a dashboard backend. No credentials are required to inspect or reproduce the documented flow beyond standard tool installations.

## Further reading

- Threat model and verified controls: `docs/security/THREAT_MODEL.md`
- Trust boundaries: `docs/security/TRUST_BOUNDARIES.md`
- Safety, approval model, and patch policy: `docs/security/SAFETY.md`
- Untrusted inputs, AI risks, and credential hygiene: `docs/security/INPUT_AND_AI_RISKS.md`
- Evidence integrity: `docs/security/EVIDENCE_INTEGRITY.md`

These documents are documentation-level audits; they do not add security controls.
