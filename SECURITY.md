# Security Policy

## Reporting a vulnerability

Do not open a public issue for credentials, exploitable vulnerabilities, private data, or instructions that would enable immediate harm. Report the matter privately to the repository owner through GitHub's private vulnerability reporting feature when available. If that feature is unavailable, contact the owner through a previously verified private channel.

Include the affected component, reproducible conditions, realistic impact, and a safe remediation suggestion. Do not include live secrets or unnecessary personal data.

## Supported versions

Until formal releases are declared, only the current default branch is maintained. Experimental branches and archived snapshots are unsupported unless explicitly stated.

## Response principles

- Preserve evidence and relevant audit records.
- Revoke exposed credentials and capabilities promptly.
- Prefer containment and reversible remediation.
- Do not retaliate against good-faith reporters.
- Do not publicly disclose an unpatched high-severity issue.
- Treat uncertainty about authorization as denial.

## Secret handling

Never commit passwords, tokens, private keys, seed phrases, environment files, production credentials, or unredacted sensitive datasets. Rotate a secret immediately if it reaches repository history.
Report suspected vulnerabilities privately through the repository owner's verified GitHub contact method. Do not publish credentials, private data, exploit instructions, or unpublished research in an issue.

Never commit passwords, tokens, private keys, environment files, production credentials, or unredacted personal data. Reviewers and contributors must use pull requests, preserve attribution and provenance, and keep simulations and security tests non-destructive.

The Commons Initiative retains ownership of original code, documentation, research artifacts, and inventions. Review access does not transfer ownership or grant commercial, patent, copyright, or relicensing rights.
