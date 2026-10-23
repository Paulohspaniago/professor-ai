import hashlib
import json
from pathlib import Path

import pytest

from professor_ai.evaluation.runner import run_evaluation


class ScriptedProvider:
    name = "test-provider"
    fingerprint = hashlib.sha256(b"test-provider-v1").hexdigest()

    def __init__(self, mode="ok"):
        self.mode = mode
        self.calls = []

    def retrieve(self, request, sources):
        self.calls.append(("retrieve", request, sources))
        if request.language == "en":
            if self.mode == "retrieve_error":
                raise RuntimeError("Retrieval unavailable")
            if self.mode == "wrong_language":
                return ["square-pt"]
            if self.mode == "unknown":
                return ["unknown"]
            if self.mode == "duplicate":
                return ["square-en", "square-en"]
            if self.mode == "malformed_retrieval":
                return {"not": "a list"}
        return [source.id for source in sources]

    def generate(self, request, evidence):
        self.calls.append(("generate", request, evidence))
        if request.language == "en":
            if self.mode == "generate_error":
                raise RuntimeError("Generation unavailable")
            if self.mode == "empty":
                return {"status": "answered", "text": "", "citations": []}
            if self.mode == "bad_citation":
                return {"status": "answered", "text": "An answer", "citations": ["square-pt"]}
            if self.mode == "duplicate_citation":
                return {"status": "answered", "text": "An answer", "citations": ["square-en"] * 2}
            if self.mode == "cancel":
                raise KeyboardInterrupt
        return {"status": "answered", "text": "An answer", "citations": [e.id for e in evidence]}


def test_pending_review_blocks_before_provider_calls(evaluation_root: Path) -> None:
    provider = ScriptedProvider()
    with pytest.raises(ValueError, match="human review"):
        run_evaluation(evaluation_root, provider)
    assert provider.calls == []


def test_scoped_provider_input_excludes_annotations(evaluation_root: Path) -> None:
    manifest_path = evaluation_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for field, value in [("collection", "unselected"), ("subject", "physics")]:
        distractor = dict(manifest["documents"][0])
        distractor.update(id=f"distractor-{field}", path=f"corpus/distractor-{field}.md")
        distractor[field] = value
        (evaluation_root / distractor["path"]).write_bytes(
            (evaluation_root / "corpus/square.en.md").read_bytes()
        )
        manifest["documents"].append(distractor)
    manifest_path.write_text(json.dumps(manifest))
    provider = ScriptedProvider()
    report = run_evaluation(evaluation_root, provider, allow_unreviewed=True)

    assert [c[0] for c in provider.calls] == ["retrieve", "generate", "retrieve", "generate"]
    for _, request, evidence in provider.calls:
        assert set(type(request).model_fields) == {
            "id",
            "question",
            "language",
            "selected_collections",
        }
        assert evidence
        assert all(e.language == request.language for e in evidence)
        assert all(e.collection in request.selected_collections for e in evidence)
        assert all(e.subject == "mathematics" for e in evidence)
    assert report.summary.total == 2
    assert report.summary.status_matches.numerator == 2
    assert report.summary.status_matches.denominator == 2
    assert report.summary.evidence_recall.value == 1
    assert report.metadata.unreviewed_case_ids
    assert report.human_metrics == {
        "correctness": None,
        "citation_support": None,
        "citation_coverage": None,
    }
    assert not report.benchmark_qualified
    for result in report.results:
        assert result.timings.retrieval_ms >= 0
        assert result.timings.generation_ms >= 0
        assert result.timings.total_ms >= 0
        assert result.reference_answer


@pytest.mark.parametrize(
    "mode,stage",
    [
        ("retrieve_error", "retrieval"),
        ("wrong_language", "retrieval"),
        ("unknown", "retrieval"),
        ("duplicate", "retrieval"),
        ("malformed_retrieval", "retrieval"),
        ("generate_error", "generation"),
        ("empty", "generation"),
        ("bad_citation", "generation"),
        ("duplicate_citation", "generation"),
    ],
)
def test_failed_cases_stay_in_denominators_and_later_cases_run(evaluation_root, mode, stage):
    provider = ScriptedProvider(mode)
    report = run_evaluation(evaluation_root, provider, allow_unreviewed=True)

    assert report.summary.total == 2
    assert report.summary.errors == 1
    assert report.summary.status_matches.numerator == 1
    assert report.summary.status_matches.denominator == 2
    assert report.summary.evidence_recall.denominator == 2
    assert report.results[0].error.stage == stage
    assert report.results[1].error is None
    assert report.by_language["en"].errors == 1
    assert report.by_subject["mathematics"].total == 2
    if stage == "retrieval":
        assert report.results[0].timings.generation_ms is None
        assert len(provider.calls) == 3
        assert report.summary.evidence_recall.value == 0.5


def test_cancellation_is_not_swallowed(evaluation_root):
    with pytest.raises(KeyboardInterrupt):
        run_evaluation(evaluation_root, ScriptedProvider("cancel"), allow_unreviewed=True)


def test_no_required_evidence_does_not_create_perfect_recall(evaluation_root):
    path = evaluation_root / "cases/smoke.json"
    cases = json.loads(path.read_text())
    for case in cases:
        case.update(
            category="insufficient_evidence",
            expected_status="insufficient_evidence",
            required_evidence_ids=[],
            missing_information=["Unknown input"],
        )
    path.write_text(json.dumps(cases))
    report = run_evaluation(evaluation_root, ScriptedProvider(), allow_unreviewed=True)

    assert report.summary.evidence_recall.denominator == 0
    assert report.summary.evidence_recall.value is None
    assert report.summary.status_matches.numerator == 0


def test_fingerprints_capture_configuration_and_input_changes(evaluation_root):
    provider = ScriptedProvider()
    first = run_evaluation(evaluation_root, provider, allow_unreviewed=True, project_revision="abc")
    repeat = run_evaluation(
        evaluation_root, provider, allow_unreviewed=True, project_revision="abc"
    )
    assert first.metadata.configuration_fingerprint == repeat.metadata.configuration_fingerprint
    provider.fingerprint = hashlib.sha256(b"changed").hexdigest()
    changed = run_evaluation(
        evaluation_root, provider, allow_unreviewed=True, project_revision="abc"
    )
    assert changed.metadata.configuration_fingerprint != first.metadata.configuration_fingerprint
    assert changed.metadata.dataset_fingerprint == first.metadata.dataset_fingerprint


def test_changed_sources_fail_before_provider_execution(evaluation_root):
    (evaluation_root / "corpus/square.en.md").write_text("changed")
    provider = ScriptedProvider()
    with pytest.raises(ValueError, match="hash"):
        run_evaluation(evaluation_root, provider, allow_unreviewed=True)
    assert not provider.calls
