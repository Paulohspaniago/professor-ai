# Development Guide

The implemented foundation is an installable Python package with configuration, read-only diagnostics, and a local health API. Document ingestion, retrieval, model inference, and the web interface are later roadmap work.

## Requirements and setup

- Python 3.12. The project deliberately qualifies this minor version first.
- uv; CI and the initial local validation use version 0.11.16.
- Git. Node is not required until frontend development begins.

Install uv using its [official installation guide](https://docs.astral.sh/uv/getting-started/installation/). From the repository root:

```bash
uv sync --locked --group dev
uv run professor-ai doctor
uv run professor-ai doctor --json
```

uv can install the Python version selected by `.python-version` if it is missing. Initial interpreter and dependency setup needs network access. The lockfile records package versions and artifact hashes; commit intentional lockfile changes with the dependency change. Do not edit generated lock entries by hand.

No model is required or downloaded. A successful doctor report says the **foundation environment** is ready; it does not claim an AI model is ready. Required checks cover Python 3.12, working SQLite FTS5, and writable data-directory ancestry. The model check is optional and currently reports `missing`.

Diagnostics use an in-memory SQLite database and inspect permissions without creating the data directory or modifying existing documents. Writability is advisory: a later operation can still fail if permissions, quota, or available storage change.

## Start the local API

```bash
uv run professor-ai serve
```

In another terminal:

```bash
curl http://127.0.0.1:8765/health
```

Expected response:

```json
{"status":"ok","version":"0.1.0.dev0","model_status":"not_configured"}
```

Stop the server with Ctrl+C. Health reports process availability, independently of model readiness. Interactive Swagger/ReDoc pages are disabled so this foundation does not load documentation assets from external CDNs. The OpenAPI JSON remains available at `/openapi.json`.

## Configuration

Only explicitly prefixed environment variables configure the application. `.env` files are not loaded automatically.

| Variable | Default | Behavior |
| --- | --- | --- |
| `PROFESSOR_AI_DATA_DIR` | Platform-specific per-user data directory for ProfessorAI | Optional path override, including spaces and non-ASCII names; not created by health or doctor |
| `PROFESSOR_AI_HOST` | `127.0.0.1` | This milestone rejects every other bind address |
| `PROFESSOR_AI_PORT` | `8765` | Integer from 1 through 65535 |

Example for macOS/Linux:

```bash
PROFESSOR_AI_PORT=9876 uv run professor-ai serve
```

`doctor` exits 0 when all required checks pass and 1 when blocked. `doctor --json` keeps its report machine-readable even for invalid application configuration. `serve` rejects invalid settings with exit code 2 before opening a listener. If the chosen port is already occupied, stop the process you own or choose another port.

If FTS5 is missing, use an appropriate Python build; the uv-managed 3.12 build is the initial tested path. If data access is blocked, correct permissions or point `PROFESSOR_AI_DATA_DIR` to an accessible directory. Do not solve local setup problems by opening the server to the network.

## Required checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src/professor_ai
uv run pytest -q
uv run python scripts/check_docs.py
uv run python scripts/check_evals.py --check-review-packet
```

The default test suite disables network sockets using pytest-socket. Unix-domain sockets are allowed for local event-loop machinery; external TCP connections are blocked. Configuration tests remove inherited `PROFESSOR_AI_` variables, and storage-related tests use temporary directories rather than real learning material.

After setup, use `uv run --offline --no-sync pytest -q` to run the installed suite without uv dependency resolution. Do not use `--no-sync` before installing the locked environment or after changing dependencies.

CI runs formatting, lint, strict typing, network-blocked tests, and documentation validation on Linux and macOS with Python 3.12. Real-model qualification remains a separately marked, future suite. These checks do not establish RAG quality or Apple Silicon inference performance.

## Development evaluation fixtures

The [smoke corpus](../evals/README.md) contains 30 bilingual proposals and original
source notes, with annotations stored outside the retrieval corpus. Read the
[review packet](../evals/REVIEW.md) to review expected behavior. The fixture check
above verifies structure, hashes, scope, translation metadata, and packet freshness.
It does not run a model or establish answer quality. Use `--require-reviewed` to
enforce recorded human approvals; it intentionally fails while proposals remain.
After editing annotations, run `uv run python scripts/check_evals.py
--write-review-packet` on one line and commit the refreshed packet.

## Contribution workflow

Use a branch and a pull request against `main`, follow [CONTRIBUTING.md](../CONTRIBUTING.md), and reference the relevant [roadmap story](ROADMAP.md). Keep setup commands accurate, tests focused on behavior, and private files out of commits. For a clean-environment check, install the committed checkout in a new temporary directory instead of reusing an existing `.venv`.
