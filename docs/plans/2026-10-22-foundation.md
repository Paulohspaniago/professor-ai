# Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task when those workflows are available. Human contributors can follow the same task checklists directly.

**Goal:** Make a clean checkout installable, diagnosable, and testable without a model download, completing S01.02 and S01.03.

**Architecture:** A small Python package owns validated settings, the API lifecycle, and a CLI. Core checks run without network access or model dependencies. This foundation introduces no retrieval, generation, or frontend implementation.

**Tech Stack:** Python 3.12, uv, FastAPI, Pydantic 2, pydantic-settings, platformdirs, Typer, Uvicorn; Ruff, mypy, pytest, HTTPX, GitHub Actions.

**Spec:** [Architecture](../ARCHITECTURE.md), with product scope and story acceptance in the [roadmap](../ROADMAP.md#e01--foundation-and-community).

**Implementation status:** Implemented on 2026-10-23. Configuration, health, diagnostics, CLI, clean-checkout installation, offline checks, and wheel build were validated. The checklist below records the execution; ongoing commands are maintained in [DEVELOPMENT.md](../DEVELOPMENT.md).

## Global Constraints

- Code, identifiers, comments, commits, and technical documentation are in English.
- Initial reference hardware is the maintainer's reported Apple M4-family MacBook with 16 GB RAM; hardware performance remains unmeasured.
- Python 3.12 is the initial development interpreter. Pin dependency versions through uv.lock after resolving and testing them.
- The application serves one local user and binds to `127.0.0.1` by default; this milestone rejects other bind addresses.
- Private data lives outside the repository by default. `PROFESSOR_AI_DATA_DIR` may override that path.
- Normal operation must work offline after explicit dependency/model setup; the foundation's tests require no model or external network.
- Node 22.12+ and a committed npm lockfile become requirements when the frontend is introduced in E08; do not create an unused frontend package now.
- The repository remains MIT-licensed. Do not commit private data or model binaries.

## Review Focus

- A data-directory path contains spaces or non-ASCII characters: preserve it without shell interpolation (Task 2).
- A user requests a non-loopback bind address or invalid port: reject settings before listening (Task 2).
- SQLite lacks FTS5: diagnostics report the missing capability with an actionable failure (Task 3).
- Models are not installed: foundation health/diagnostics remain useful and no download starts (Tasks 2–3).
- CI starts from a clean checkout: declared dependencies and locks are sufficient without local caches (Task 4).

## Planned file ownership

| Location | Responsibility |
| --- | --- |
| pyproject.toml, uv.lock, .python-version | Package metadata, dependency resolution, tool configuration |
| src/professor_ai/__init__.py | Package version |
| src/professor_ai/settings.py | Validated application settings and local data path |
| src/professor_ai/app.py | FastAPI composition and health response |
| src/professor_ai/doctor.py | Capability probes and typed diagnostic report |
| src/professor_ai/cli.py | `doctor` and `serve` commands |
| tests/unit/test_settings.py | Configuration boundaries |
| tests/unit/test_doctor.py | Required versus optional capabilities |
| tests/integration/test_health.py | HTTP health contract without models |
| tests/integration/test_cli.py | CLI exit codes and diagnostics |
| scripts/check_docs.py | Existing local Markdown link and roadmap validation |
| .github/workflows/ci.yml | Reproducible automated checks |
| docs/DEVELOPMENT.md | Commands proven against the implemented environment |

The application paths below were implemented in this delivery. The existing documentation checker was reused and adjusted to exclude generated caches and local planning scratch.

## Task 1: Create the installable package

**Files:** create `pyproject.toml`, `uv.lock`, `.python-version`, and `src/professor_ai/__init__.py`; update `.gitignore` only if actual tools add outputs.

**Interfaces:** produces an installable `professor_ai` package with `__version__ = "0.1.0.dev0"`. Later tasks add the `professor-ai` console entry point. No model package is a required dependency at this stage.

- [x] Define the `src/` package layout, Python 3.12 baseline, MIT metadata, runtime dependencies, and a `dev` dependency group containing Ruff, mypy, pytest, and HTTPX.
- [x] Configure Ruff formatting/lint rules and mypy for the package; use pytest's `tests/` discovery. Configure only checks that will actually run.
- [x] Resolve dependencies using uv, commit the generated lockfile, and install with `uv sync --locked --group dev`.
- [x] Run `uv run python -c 'import professor_ai; print(professor_ai.__version__)'`; expect `0.1.0.dev0` with exit code 0.
- [x] Review the dependency tree for unexpected heavy inference packages, then commit this independently reviewable bootstrap.

This task is package configuration; it needs an installation check, not a test that merely repeats metadata.

## Task 2: Validate settings and provide model-independent health

**Files:** create `src/professor_ai/settings.py`, `src/professor_ai/app.py`, `tests/unit/test_settings.py`, and `tests/integration/test_health.py`.

**Interfaces:** `Settings` has `data_dir: Path`, `host: Literal["127.0.0.1"] = "127.0.0.1"`, and `port: int = 8765` constrained to 1–65535. `load_settings() -> Settings` reads `PROFESSOR_AI_`-prefixed environment variables and defaults `data_dir` using `platformdirs.user_data_path("ProfessorAI", appauthor=False)`. `create_app(settings: Settings) -> FastAPI` exposes `GET /health`.

- [x] Write settings tests for the default loopback address, port bounds, a temporary data path containing spaces/accents, and rejection of `0.0.0.0`. Assert validation failures rather than matching incidental exception wording.
- [x] Write a health test using HTTPX/FastAPI's test client. Assert status 200 and exactly `{"status": "ok", "version": "0.1.0.dev0", "model_status": "not_configured"}`. Assert no model download or data-directory creation occurs merely by importing the app or requesting health.
- [x] Run `uv run pytest tests/unit/test_settings.py tests/integration/test_health.py -q`; confirm failures are due to the missing behavior.
- [x] Implement the two modules and their typed interfaces. Configuration validation must happen before any server starts. A healthy API is not reported as a ready inference engine.
- [x] Run the same tests; expect all passing. Run `uv run mypy src/professor_ai` and `uv run ruff check .`; resolve real failures and commit.

## Task 3: Add useful diagnostics and a local server command

**Files:** create `src/professor_ai/doctor.py`, `src/professor_ai/cli.py`, `tests/unit/test_doctor.py`, and `tests/integration/test_cli.py`; update the console entry point in `pyproject.toml` and regenerate the lock only if dependencies change.

**Interfaces:** `CapabilityCheck` contains `name: str`, `required: bool`, `status: Literal["ok", "missing", "error"]`, and `message: str`. `DiagnosticReport` contains `status: Literal["ready", "blocked"]` and `checks: list[CapabilityCheck]`. `inspect_environment(settings: Settings) -> DiagnosticReport` probes the Python version, SQLite FTS5 using a temporary in-memory table, and the nearest existing parent of the configured data directory for write access. The report includes an optional missing-model check. `cli.app` is a Typer application providing `professor-ai doctor --json` and `professor-ai serve`.

- [x] Write tests: missing FTS5 blocks readiness; a missing optional model does not; an unwritable data parent blocks readiness; diagnostics do not modify the user's data. Inject probe results where host-dependent behavior would make tests nondeterministic.
- [x] Write CLI tests for JSON matching the report schema, exit code 0 on readiness and 1 on blocked diagnostics, and invalid settings failing before `serve` invokes Uvicorn. Verify `serve` passes the validated loopback host and port to the runner.
- [x] Run `uv run pytest tests/unit/test_doctor.py tests/integration/test_cli.py -q`; confirm the expected failures.
- [x] Implement diagnostics and CLI commands. Error messages explain what is missing and which documented setup step resolves it. Keep model management out of this task.
- [x] Run those tests, then run `uv run professor-ai doctor --json` on the development machine. Record the actual capability report; do not hard-code a successful result into documentation.
- [x] Start `uv run professor-ai serve`, request `/health` locally, and stop the owned process. Confirm the health contract and clean shutdown, then commit.

## Task 4: Make the foundation reproducible in CI and documentation

**Files:** create `.github/workflows/ci.yml` and `docs/DEVELOPMENT.md`; reuse `scripts/check_docs.py` and preserve the existing `.github/workflows/docs.yml`; update `README.md` and `CONTRIBUTING.md` with commands verified in Tasks 1–3.

**Interfaces:** `python scripts/check_docs.py` returns 0 when local Markdown targets and fragments resolve and nonzero with file/line diagnostics otherwise. It ignores external URLs and explicitly marked illustrative source paths. No network requests are required.

- [x] Run the existing documentation checker and extend it only if application documentation introduces unsupported link forms. Check changed behavior against a temporary missing-target fixture and a known-valid fixture. Do not add application tests solely for documentation wording.
- [x] Configure CI on Linux and macOS with Python 3.12, a pinned uv version, and actions pinned to verified revisions. Install with `uv sync --locked --group dev` and run the commands below.
- [x] Run `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy src/professor_ai`, `uv run pytest -q`, and `uv run python scripts/check_docs.py`; expect zero failures.
- [x] Repeat installation and those checks in a clean temporary checkout without the current virtual environment. Confirm tests make no external network requests and do not read a real user database.
- [x] Document the proven install, doctor, serve, and check commands. State that retrieval/generation remain unimplemented. Add no passing-build badge until the public workflow actually passes.
- [x] Commit and attach check output to the PR for S01.02/S01.03. Only mark those stories done after reviewing their acceptance criteria.

## Handoff and subsequent plans

This plan completes the application foundation only. GitHub/community setup is tracked separately in S01.04 and can precede it. E02 handles evaluation data; E03 handles model artifacts and real inference. Those subsystem plans should be written with the contracts and failures learned from this foundation, rather than pretending the entire roadmap is implementation-ready today.

Recommended initial execution: implement these four tasks in order in one checkout, with review at each coherent change. Parallel work becomes useful for independently owned evaluation fixtures or UI work once shared contracts exist. This document does not authorize publishing a remote repository or downloading model weights by itself; those actions follow the user's execution request and the relevant story scope.
