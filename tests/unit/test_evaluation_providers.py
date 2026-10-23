import json

import pytest

from professor_ai.evaluation.fixtures import load_dataset
from professor_ai.evaluation.providers import AbstainingProvider, ReplayProvider
from professor_ai.evaluation.runner import run_evaluation


def replay(root, path):
    bundle = load_dataset(root)
    return ReplayProvider(
        path, dataset_fingerprint=bundle.fingerprint, case_ids={case.id for case in bundle.cases}
    )


def test_abstention_is_a_bilingual_baseline_without_fake_retrieval(evaluation_root):
    report = run_evaluation(evaluation_root, AbstainingProvider(), allow_unreviewed=True)
    assert report.summary.total == 2
    assert report.summary.status_matches.value == 0
    assert report.summary.evidence_recall.value == 0
    assert report.results[0].answer.status == "insufficient_evidence"
    assert report.results[0].answer.text != report.results[1].answer.text
    assert not report.results[0].selected_evidence_ids


def test_replay_runs_recorded_outputs_with_a_stable_file_identity(evaluation_root, replay_path):
    provider = replay(evaluation_root, replay_path)
    report = run_evaluation(evaluation_root, provider, allow_unreviewed=True)
    assert report.summary.status_matches.value == 1
    assert report.summary.errors == 0
    assert len(provider.fingerprint) == 64
    assert replay(evaluation_root, replay_path).fingerprint == provider.fingerprint


@pytest.mark.parametrize("field,value", [("schema_version", 2), ("dataset_fingerprint", "stale")])
def test_replay_rejects_wrong_version_or_dataset(evaluation_root, replay_path, field, value):
    payload = json.loads(replay_path.read_text())
    payload[field] = value
    replay_path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        replay(evaluation_root, replay_path)


def test_unknown_replay_case_ids_are_configuration_errors(evaluation_root, replay_path):
    payload = json.loads(replay_path.read_text())
    payload["results"]["unknown"] = next(iter(payload["results"].values()))
    replay_path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="unknown"):
        replay(evaluation_root, replay_path)


@pytest.mark.parametrize("mode,stage", [("missing", "retrieval"), ("malformed", "generation")])
def test_missing_and_malformed_cases_are_recorded_without_dropping_samples(
    evaluation_root, replay_path, mode, stage
):
    payload = json.loads(replay_path.read_text())
    if mode == "missing":
        del payload["results"]["smoke-math-01-en"]
    else:
        payload["results"]["smoke-math-01-en"]["answer"] = {"status": "answered"}
    replay_path.write_text(json.dumps(payload))
    report = run_evaluation(
        evaluation_root, replay(evaluation_root, replay_path), allow_unreviewed=True
    )
    assert report.summary.errors == 1
    assert report.summary.status_matches.denominator == 2
    assert report.results[0].error.stage == stage
    assert report.results[1].error is None


def test_replay_fingerprint_changes_when_output_text_changes(evaluation_root, replay_path):
    before = replay(evaluation_root, replay_path).fingerprint
    payload = json.loads(replay_path.read_text())
    payload["results"]["smoke-math-01-en"]["answer"]["text"] = "Changed output"
    replay_path.write_text(json.dumps(payload))
    assert replay(evaluation_root, replay_path).fingerprint != before


def test_loaded_replay_cannot_run_against_a_changed_dataset(evaluation_root, replay_path):
    provider = replay(evaluation_root, replay_path)
    path = evaluation_root / "cases/smoke.json"
    cases = json.loads(path.read_text())
    cases[0]["question"] += " Explain."
    path.write_text(json.dumps(cases))

    with pytest.raises(ValueError, match="dataset fingerprint"):
        run_evaluation(evaluation_root, provider, allow_unreviewed=True)
