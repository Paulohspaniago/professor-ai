# Repository Maintenance Policy

Repository: [Paulohspaniago/professor-ai](https://github.com/Paulohspaniago/professor-ai). Maintainer: [Paulo Paniago](https://github.com/Paulohspaniago). Project code and original documentation use the [MIT license](../LICENSE).

## Initial public setup

The public repository includes project documentation, documentation tooling, and the Python application foundation. It is not a stable study-assistant release. Issues and Discussions are enabled; the separate GitHub wiki is disabled so documentation stays versioned with the project.

`main` is the default branch. Contributions use pull requests, required checks,
resolved review conversations, and a linear history. The required checks are
`Documentation checks`, `Python checks (ubuntu-latest)`, and
`Python checks (macos-latest)`, with branches required to be up to date. Force
pushes and branch deletion are blocked. Squash is the enabled merge method, and
merged feature branches are automatically deleted.

Protection applies to administrators as well. The initial policy requires a PR and passing checks but zero mandatory approvals, allowing the sole maintainer to merge their own passing PRs. CODEOWNERS identifies the maintainer for review requests; a mandatory self-approval is not required. Increase the required approval count when there is another active reviewer. External contributors cannot merge without repository write access.

## Automation

The `Documentation checks` job validates local Markdown links, heading references, story IDs, and dependency cycles. It runs on pushes to `main`, pull requests, and manual dispatch. The check name is stable because branch protection references it.

GitHub Actions uses read-only default token permissions and cannot approve pull requests. Actions are pinned to full official commit revisions, and checkout does not persist credentials. Fork workflows require approval for outside contributors. Dependabot proposes GitHub Actions and uv dependency updates weekly.

Repository security settings include Dependabot vulnerability alerts, automated security fixes, secret scanning and push protection, and private vulnerability reporting where GitHub makes them available. Report actual feature availability when applying this policy; do not claim an unavailable feature is enabled. See [SECURITY.md](../SECURITY.md) for reporting instructions.

The Python workflow checks formatting, lint, strict typing, network-blocked behavior
tests, documentation, and development-fixture integrity/review-packet freshness on
Linux and macOS with Python 3.12. Documentation integrity retains its separate
check. Draft fixture checks do not imply human approval; the explicit human-review
gate is documented in [evals/README.md](../evals/README.md). Neither workflow
establishes retrieval quality or model performance; release evaluations remain
E02/E09 work.

## Work organization

Milestones mirror M0–M6 from the [roadmap](ROADMAP.md). Labels identify stories, priority, subsystem, documentation, dependencies, and approachable contributions. Start with the ready foundation and evaluation work; retain the full 44-story backlog in the roadmap until each story is ready to become an issue.

Initial contribution paths:

- [S01.02: Python application foundation (completed)](https://github.com/Paulohspaniago/professor-ai/issues/2)
- [S02.01: Reviewed learning corpus](https://github.com/Paulohspaniago/professor-ai/issues/3)
- [First contribution: one bilingual physics fixture](https://github.com/Paulohspaniago/professor-ai/issues/4)

The maintainer owns triage, technical decisions, contributor access, and release publication. CI passing is necessary but not sufficient for acceptance. Review behavior and evidence before merging, and keep the roadmap's completion state accurate.

## Repository versus local configuration

Use a GitHub no-reply email for public commits if you do not want to publish a personal address. Machine-local Git identity and authentication settings do not belong in the repository. Do not store credentials in remotes, commit messages, issues, or documentation.

Changes to protection, token permissions, or release automation should be documented in the relevant PR. Test the workflow successfully before adding a new required check to avoid blocking every contribution.
