# Contributing to Professor AI

Thank you for helping build a local, evidence-based study assistant. The project is currently in its planning stage. Documentation checks are available; the application development environment and its CI remain tracked under [E01](docs/ROADMAP.md#e01--foundation-and-community).

## Choose a contribution

Use the stable story IDs in the [roadmap](docs/ROADMAP.md) and check the [open issues](https://github.com/Paulohspaniago/professor-ai/issues). Each ready story can become an issue. Check with the maintainer before beginning a large change so contributors do not duplicate work. Documentation, accessible UI behavior, parser fixtures, and human-reviewed English/Portuguese evaluation cases are useful contributions.

## Documentation workflow

Fork the repository, create a short-lived branch, and submit a pull request against `main`. Run the documentation checks with Python 3.10 or newer; no package installation or model download is needed for this command:

```bash
python3 scripts/check_docs.py
```

This checks local Markdown links, heading references, story IDs, and roadmap dependency cycles. The GitHub Actions workflow also checks commit whitespace. It does not evaluate application behavior or model quality. The future application development interpreter remains Python 3.12.

## Working conventions

- Write code, identifiers, comments, commits, issues, and technical documentation in English. Preserve original language inside source fixtures and evaluation questions.
- Keep a PR focused on one story or a small, coherent change; reference its story ID.
- Explain the user-visible behavior, relevant decisions, and validation results.
- Add behavior tests for meaningful application changes. Documentation-only changes need link and consistency checks, not artificial application tests.
- Keep model revisions, runtime versions, and dependency lockfiles reproducible.
- Never commit personal documents, local databases, credentials, model binaries, or unredacted private benchmark traces.
- Include origin and redistribution terms with contributed learning materials or datasets. Our MIT license does not override their terms.
- Do not report estimated latency or generated evaluation labels as measured, human-reviewed results.

## Before a pull request

Verify the acceptance criteria of the linked story, update affected documentation, and record which checks ran. When the foundation is implemented, its documented lint, typing, and test commands become the required baseline. There is no application installation command yet.

Changes to persistence formats, public contracts, dependencies, or model defaults should include a short decision record explaining alternatives and migration effects. A model default change also needs the comparison described in [EVALUATION.md](docs/EVALUATION.md).

## Collaboration

Discuss ideas respectfully, give actionable feedback, and make room for people learning the project. The maintainer decides roadmap priority and reviews releases. Follow the [code of conduct](CODE_OF_CONDUCT.md); report vulnerabilities through the private route in [SECURITY.md](SECURITY.md). See the [repository maintenance policy](docs/REPOSITORY.md) for branch, automation, and dependency settings.
