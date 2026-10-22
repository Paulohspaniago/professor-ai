# Security Policy

## Project status and supported versions

Professor AI is currently in planning and foundation development. There is no released application or stable version. Security reports about repository automation, dependency handling, and published project artifacts are welcome. A supported-version table will be added with the first application release.

## Report a vulnerability privately

Use [GitHub's private vulnerability reporting form](https://github.com/Paulohspaniago/professor-ai/security/advisories/new). This sends the report to repository maintainers without creating a public issue.

Include the affected commit or version, reproduction steps, impact, and a minimal example. Use synthetic or redacted inputs. Do not attach private learning materials, credentials, personal data, or unrelated system files.

Please coordinate disclosure with the maintainer while a report is assessed. This is a volunteer-maintained project and does not promise a fixed response time or a paid bounty.

## Current security expectations

- Workflows receive read-only repository permissions unless a documented task requires more.
- Third-party Actions are pinned to full commit revisions; Dependabot proposes updates.
- Private documents, local databases, model binaries, and credentials are excluded from source control.
- Future application code must honor the local-access and offline boundaries in the [architecture](docs/ARCHITECTURE.md).

For ordinary bugs or incorrect educational answers without a security impact, use the public bug report template. For conduct concerns, follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
