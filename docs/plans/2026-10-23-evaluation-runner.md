# Evaluation Runner Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement the tasks, with a fresh whole-branch review at the end.

**Goal:** Run fixed development cases through replaceable offline providers and preserve inspectable results, failures, timings, and fingerprints.

**Architecture:** The runner owns annotations; providers receive only questions and scoped source text. Typed results feed mechanical diagnostics and JSON/Markdown reports. The CLI supports an abstention baseline and replayed pipeline outputs, never model-quality certification.

**Tech Stack:** Existing Python 3.12, Pydantic, Typer, pytest, and standard library; no new dependencies.

**Spec:** [S02.02](../ROADMAP.md#s0202--build-the-evaluation-runner), [evaluation design](../EVALUATION.md), and [fixture contracts](../../evals/README.md).

## Design decisions

The maintainer asked to continue the roadmap. These implementation choices are the
builder's decisions, using the existing project contracts:

- A provider protocol plus replay files lets tests exercise the harness before RAG exists. Building an actual retriever now would mix S02.02 with E05/E06; adding an LLM judge would not satisfy the human grading policy.
- Two provider stages, retrieve and generate, expose stage failures and timings. Providers receive no reference answer, rubric, expected status, or annotation evidence IDs.
- The abstention provider retrieves nothing and always returns insufficient evidence. Replay files reproduce externally recorded outputs; their hash and dataset binding are recorded. Neither is an AI model.
- Default execution requires recorded human review. `--allow-unreviewed` explicitly permits development use of proposals and labels the report accordingly. S02.01 remains open; tooling can progress while its acceptance is pending.
- Status agreement and evidence recall are mechanical diagnostics. Correctness and citation support/coverage stay ungraded; this harness cannot qualify a release, even with a perfect synthetic replay.
- Failed cases remain in all applicable denominators, including per-language/subject summaries. Retrieval failure prevents generation for that case, but does not stop other cases. Ctrl+C remains cancellation.
- Report directories must be new and outside the dataset; existing files and linked targets cannot be overwritten. Schema version 1 is new, with no legacy report migration. Future incompatible changes must bump the version.

## Global Constraints

- Preserve the 30 proposals and their pending human reviews unchanged.
- Technical documentation and code are English; source/question text preserves its language.
- No model download, network access, new dependency, or database is required.
- Hash and validate allowlisted source bytes before supplying text to providers.
- Scope source text and returned evidence/citations to the selected collection, subject, and language.
- Record project revision (or explicit unknown), dirty state when discoverable, package/Python/platform versions, provider configuration fingerprint, dataset fingerprint, and per-stage times.
- Model artifacts, tokenizer, prompt, and index generation are explicitly absent for these synthetic providers.

## Review Focus

- Invalid or out-of-scope evidence/citations must fail a case without reaching a provider with unauthorized source text.
- Exceptions or malformed outputs must retain cases in totals and record the stage; later cases still run.
- A changed source/replay file must fail integrity/binding checks or change fingerprints before results are used.
- Zero-evidence cases must not divide by zero; ungraded human metrics must not appear as perfect scores.
- Output paths, including symlink aliases, must not overwrite existing runs or dataset inputs.

## Task 1: Runner contracts and mechanical diagnostics

**Files:** create `src/professor_ai/evaluation/run_models.py`, `runner.py`, and `tests/unit/test_evaluation_runner.py`.

**Interfaces:** `EvaluationProvider` exposes `name`, `fingerprint`, `retrieve(request: EvaluationRequest, sources: tuple[Evidence, ...]) -> object`, and `generate(request, evidence) -> object`. `run_evaluation(root: Path, provider: EvaluationProvider, *, allow_unreviewed: bool = False, project_revision: str = "unknown", working_tree_dirty: bool | None = None) -> RunReport` validates fixtures, runs stages, and aggregates all cases. Raw provider outputs are validated at stage boundaries.

- [x] Write tests for the review gate, source scope/no annotation leakage, ordered stage execution, retrieval/generation exceptions, malformed output, duplicate/unknown/cross-language evidence and citations, per-group denominators, timing fields, and configuration fingerprints.
- [x] Run `uv run pytest tests/unit/test_evaluation_runner.py -q`; expect missing implementation failure.
- [x] Implement typed requests/evidence/answers, provider protocol, isolated case execution, honest metrics, and report metadata. Use monotonic timings and existing SHA-256 contracts.
- [x] Run focused tests, strict typing, and full suite; expect all passing.
- [x] Commit `feat(evals): run scoped providers and preserve failure diagnostics`.

## Task 2: Offline providers and report artifacts

**Files:** create `providers.py`, `reporting.py`, `tests/unit/test_evaluation_providers.py`, and `tests/unit/test_evaluation_reporting.py` under their evaluation/package or test folders.

**Interfaces:** `AbstainingProvider()` implements the protocol. `ReplayProvider(path: Path, *, dataset_fingerprint: str, case_ids: set[str])` loads schema-version-1 replay JSON with `dataset_fingerprint` and a `results` mapping; each entry has `evidence_ids` and raw `answer`. Missing cases become case-level errors; unknown IDs or stale bindings reject configuration. `render_report(report: RunReport) -> str` and `write_report(report, output: Path, *, dataset_root: Path) -> None` produce `report.json` and `report.md` in a new directory.

- [x] Test baseline abstention, bilingual text, replay identity/binding, missing/malformed entries, and fingerprint changes. Test readable errors/metrics, JSON round-trip, existing outputs preserved, and dataset/symlink path rejection.
- [x] Run the new focused tests; expect missing implementation failures.
- [x] Implement providers and safe report writing. Display numerator/denominator values and explicit ungraded correctness/citation semantics in Markdown.
- [x] Run full suite and typing; expect all passing.
- [x] Commit `feat(evals): add offline replay providers and run reports`.

## Task 3: CLI, documentation, and reproducible handoff

**Files:** create `src/professor_ai/evaluation/command.py`, `tests/integration/test_evaluation_runner_cli.py`, `docs/EVALUATION_RUNNER.md`; modify `src/professor_ai/cli.py`, `README.md`, `docs/EVALUATION.md`, `docs/DEVELOPMENT.md`, and `docs/ROADMAP.md`.

**Interfaces:** `professor-ai evaluate --dataset evals --provider abstain|replay --responses PATH --output NEW_DIR --allow-unreviewed --json`. Responses are required only for replay. Defaults: dataset `evals`, abstain provider, new timestamp/UUID directory under `artifacts/evaluations`. Exit 0 means all cases completed and statuses agree; 1 means recorded case errors/status mismatches; 2 means invalid configuration, review gate, or artifact-writing failure. JSON output is a machine-readable command summary; full results live in `report.json`.

- [x] Test default review blocking without artifacts, explicit draft baseline run (all 30 cases retained), successful replay, malformed input, per-case errors, invalid provider options, path collisions, and valid JSON summaries.
- [x] Run integration tests; expect evaluate command absent.
- [x] Implement the CLI as a thin composition layer, with best-effort project revision discovery. Document commands, replay schema, metrics/limitations, output safety, and pending corpus qualification. Existing CI's full suite covers this command without a model.
- [x] Run Ruff format/lint, strict mypy, full suite, docs, fixture packet, and whitespace checks; run the actual baseline command and inspect both generated artifacts.
- [x] Commit `feat(cli): expose reproducible development evaluation runs`.

## Handoff

Obtain a fresh whole-branch review; fix Important/Critical findings with regression
tests, create a focused S02.02 issue/PR, and inspect hosted CI on the exact head.
Do not merge the new PR or mark the human corpus prerequisite complete without a
separate maintainer instruction. Keep generated run artifacts ignored.
