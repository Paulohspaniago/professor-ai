# Smoke Corpus Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans or superpowers:subagent-driven-development to execute the checklists. Human contributors can follow the same tasks directly.

**Goal:** Prepare 30 original bilingual smoke-case proposals and their source material, with reproducible validation and a readable packet for the human review required to finish S02.01.

**Architecture:** A manifest allowlists short Markdown source documents and records SHA-256 hashes, provenance, and MIT terms. JSON case annotations remain outside the retrieval corpus. A small typed loader checks integrity and generates the review packet; it does not run a model or score answers.

**Tech Stack:** Existing Python 3.12, Pydantic, pytest, and standard-library hashing/JSON; no new dependencies.

**Spec:** [Evaluation design](../EVALUATION.md) and [S02.01](../ROADMAP.md#s0201--create-the-first-reviewed-learning-corpus).

## Global Constraints

- Technical documentation and metadata are in English; learning text, questions, and reference answers preserve English or Brazilian Portuguese.
- Prepare 30 cases: ten per subject and fifteen per language, grouped into fifteen translation families.
- Cover conceptual questions, derived answers, insufficient evidence, conflicting sources, and multi-source evidence.
- Use original notes and fictional practice records under MIT. Primary references corroborate facts; their text and licenses are not copied or relicensed.
- Store source material only under `evals/corpus/`; cases, reference answers, rubrics, and review records stay outside it.
- All generated cases start with pending human review. Automated checks and AI review cannot approve them on a person's behalf.
- This dataset is development smoke material, not the 200-case frozen evaluation or a model-quality result.

## Review Focus

- An annotation points outside its selected collection: reject it before evaluation.
- A manifest path escapes the dataset, including through a symlink: reject it without reading external content.
- A source or annotation changes: fail stale source hashes and change the dataset fingerprint.
- A translated case has inconsistent numeric targets or status: reject the family.
- Draft cases pass structural checks but cannot pass the explicit human-review gate.

## Task 1: Define and test fixture contracts

**Files:** create `src/professor_ai/evaluation/__init__.py`, `src/professor_ai/evaluation/fixtures.py`, and `tests/unit/test_evaluation_fixtures.py`.

**Interfaces:** `load_dataset(root: Path) -> DatasetBundle`, `check_dataset(root: Path, *, require_reviewed: bool = False) -> ValidationReport`, and `render_review(bundle: DatasetBundle) -> str`. Pydantic records define manifest documents, coverage counts, cases, numeric targets, and explicit review metadata.

- [ ] Write small temporary dataset fixtures testing valid drafts, approved metadata requirements, broken hashes, duplicate IDs, missing evidence, collection/language isolation, path traversal/symlinks, coverage, and translation consistency.
- [ ] Run `uv run pytest tests/unit/test_evaluation_fixtures.py -q`; confirm the missing implementation fails.
- [ ] Implement strict field validation, safe allowlisted paths, coverage checks, evidence resolution, translation-family checks, and a deterministic manifest/case fingerprint.
- [ ] Run the focused tests and the full suite; expect all passing without network access.
- [ ] Commit the independently reviewable contracts and their behavior tests.

## Task 2: Author the proposed material and review packet

**Files:** create `evals/manifest.json`, `evals/corpus/{computer-science,mathematics,physics}/*.md`, `evals/cases/smoke.json`, `evals/README.md`, `evals/REVIEW.md`, and `tests/integration/test_smoke_corpus.py`.

**Interfaces:** Manifest schema version 1; split `smoke-development`; stable document IDs serve as evidence IDs because each short document is one evidence unit. Collection IDs are logical fixture names, not database UUIDs. Each case has a question, expected status/reference answer, rubric, required evidence IDs, and review record.

- [ ] Author English/Portuguese note pairs and three separate fictional conflict collections. Record primary reference URLs/check dates where applicable; fictional measurements/configuration are explicitly invented.
- [ ] Author fifteen case families, each with one English and one Portuguese case. Keep all thirty review records pending, with no fabricated reviewer or review date.
- [ ] Add an acceptance test requiring thirty cases, three subjects, balanced languages, the required scenario types, and valid source references; do not freeze pending review forever in a test.
- [ ] Generate source hashes and the readable review packet from the annotations. Confirm the packet exposes every question, answer/rubric, selected collection, and source link for human inspection.
- [ ] Run dataset checks; confirm normal structural validation passes while `require_reviewed=True` fails with all pending IDs accounted for.
- [ ] Commit the proposed data. S02.01 remains open until actual human review.

## Task 3: Integrate contributor tooling and CI

**Files:** create `scripts/check_evals.py`; modify `.github/workflows/ci.yml`, `docs/EVALUATION.md`, `docs/DEVELOPMENT.md`, `docs/ROADMAP.md`, `docs/REPOSITORY.md`, and `README.md`.

**Interfaces:** `uv run python scripts/check_evals.py` performs structural validation; `--require-reviewed` enforces the human-review gate; `--write-review-packet` regenerates `evals/REVIEW.md`; `--check-review-packet` rejects a stale packet; `--json` emits a machine-readable report.

- [ ] Exercise CLI success, malformed data, pending review, and review-packet consistency through temporary fixtures before implementation.
- [ ] Implement the thin CLI and document the separation between structural validity, recorded human review, and semantic correctness.
- [ ] Add structural/packet checks to the existing Linux/macOS jobs. Preserve the network-blocked suite and required check names.
- [ ] Run Ruff, mypy, the full tests, documentation and fixture checks, and Git whitespace checks.
- [ ] Obtain a fresh code/data review, address reproducible defects with regression tests, publish a PR referencing issue #3, and inspect hosted CI.

## Human review handoff

The maintainer or another identified human reviews the generated packet and original notes, verifies calculations and both language versions, and records approvals/corrections. An explicit review statement or reviewed PR change is needed before updating approved metadata. A generic request to continue is not an attestation that the thirty answers were reviewed. Until then, the data stays labeled draft and S02.01 remains incomplete; no model-quality claim is made.
