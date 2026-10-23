"""Keep application tests independent of the user's configuration."""

import hashlib
import json
import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in os.environ:
        if name.startswith("PROFESSOR_AI_"):
            monkeypatch.delenv(name)


@pytest.fixture
def evaluation_root(tmp_path: Path) -> Path:
    root = tmp_path / "evals"
    (root / "corpus").mkdir(parents=True)
    (root / "cases").mkdir()
    documents = []
    cases = []
    for language, suffix, question, answer in [
        ("en", "en", "What is a square?", "A rectangle with four equal sides."),
        ("pt-BR", "pt", "O que é um quadrado?", "Um retângulo com quatro lados iguais."),
    ]:
        path = f"corpus/square.{suffix}.md"
        text = f"# Square\n\n{answer}\n"
        (root / path).write_text(text, encoding="utf-8")
        documents.append(
            {
                "id": f"square-{suffix}",
                "collection": "mathematics",
                "subject": "mathematics",
                "language": language,
                "path": path,
                "sha256": hashlib.sha256(text.encode()).hexdigest(),
                "title": "Square",
                "license": "MIT",
                "authorship": "AI-assisted original fixture",
                "kind": "original_note",
                "references": [
                    {
                        "title": "Test reference",
                        "url": "https://example.org/math",
                        "checked_on": "2026-10-23",
                    }
                ],
            }
        )
        cases.append(
            {
                "id": f"smoke-math-01-{suffix}",
                "family_id": "math-01",
                "language": language,
                "subject": "mathematics",
                "category": "conceptual",
                "selected_collections": ["mathematics"],
                "question": question,
                "expected_status": "answered",
                "reference_answer": answer,
                "required_evidence_ids": [f"square-{suffix}"],
                "rubric": {"must_include": ["Four equal sides"], "must_not_include": []},
                "tags": [],
                "missing_information": [],
                "numeric_answer": None,
                "review": {
                    "status": "pending_human_review",
                    "reviewer": None,
                    "reviewed_on": None,
                    "notes": "",
                },
            }
        )
    manifest = {
        "schema_version": 1,
        "dataset_id": "test-smoke-v1",
        "split": "smoke-development",
        "case_file": "cases/smoke.json",
        "expected_counts": {
            "cases": 2,
            "languages": {"en": 1, "pt-BR": 1},
            "subjects": {"mathematics": 2},
        },
        "documents": documents,
    }
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "cases/smoke.json").write_text(json.dumps(cases), encoding="utf-8")
    return root


@pytest.fixture
def replay_path(evaluation_root: Path) -> Path:
    from professor_ai.evaluation.fixtures import load_dataset

    bundle = load_dataset(evaluation_root)
    payload = {
        "schema_version": 1,
        "dataset_fingerprint": bundle.fingerprint,
        "results": {
            case.id: {
                "evidence_ids": [f"square-{'en' if case.language == 'en' else 'pt'}"],
                "answer": {
                    "status": "answered",
                    "text": "A square has four equal sides.",
                    "citations": [f"square-{'en' if case.language == 'en' else 'pt'}"],
                },
            }
            for case in bundle.cases
        },
    }
    path = evaluation_root.parent / "replay.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path
