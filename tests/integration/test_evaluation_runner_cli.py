import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from professor_ai.cli import app

runner = CliRunner()
DATASET = Path(__file__).resolve().parents[2] / "evals"


def invoke(root, output, *args):
    return runner.invoke(
        app, ["evaluate", "--dataset", str(root), "--output", str(output), "--json", *args]
    )


def test_runner_requires_explicit_draft_override_before_writing(evaluation_root, tmp_path):
    output = tmp_path / "report"
    result = invoke(evaluation_root, output)
    assert result.exit_code == 2
    assert json.loads(result.stdout)["status"] == "invalid"
    assert "human review" in json.loads(result.stdout)["error"]
    assert not output.exists()


def test_committed_baseline_keeps_all_30_cases_and_warns_about_proposals(tmp_path):
    output = tmp_path / "smoke-run"
    result = invoke(DATASET, output, "--allow-unreviewed")
    assert result.exit_code == 1, result.output
    summary = json.loads(result.stdout)
    assert summary["status"] == "completed_with_failures"
    assert summary["case_count"] == 30
    assert "development" in result.stderr.lower()
    report = json.loads((output / "report.json").read_text())
    assert report["summary"]["status_matches"]["numerator"] == 6
    assert report["summary"]["status_matches"]["denominator"] == 30
    assert report["summary"]["evidence_recall"]["denominator"] == 24
    assert report["summary"]["errors"] == 0
    assert len(report["metadata"]["unreviewed_case_ids"]) == 30
    assert len(report["metadata"]["project_revision"]) == 40
    assert (output / "report.md").exists()


def test_successful_replay_writes_both_reports(evaluation_root, replay_path, tmp_path):
    output = tmp_path / "replayed-run"
    result = invoke(
        evaluation_root,
        output,
        "--allow-unreviewed",
        "--provider",
        "replay",
        "--responses",
        str(replay_path),
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["status"] == "completed"
    report = json.loads((output / "report.json").read_text())
    assert not report["benchmark_qualified"]
    assert report["human_metrics"]["correctness"] is None


def test_replay_errors_produce_report_and_nonzero_exit(evaluation_root, replay_path, tmp_path):
    payload = json.loads(replay_path.read_text())
    payload["results"]["smoke-math-01-en"]["answer"] = {}
    replay_path.write_text(json.dumps(payload))
    output = tmp_path / "error-run"
    result = invoke(
        evaluation_root,
        output,
        "--allow-unreviewed",
        "--provider",
        "replay",
        "--responses",
        str(replay_path),
    )
    assert result.exit_code == 1
    report = json.loads((output / "report.json").read_text())
    assert report["summary"]["errors"] == 1
    assert report["summary"]["status_matches"]["denominator"] == 2


@pytest.mark.parametrize(
    "args",
    [
        ["--provider", "unknown"],
        ["--provider", "replay"],
        ["--responses", "not-used.json"],
    ],
)
def test_invalid_provider_options_return_json_without_artifacts(evaluation_root, tmp_path, args):
    output = tmp_path / "unused"
    result = invoke(evaluation_root, output, "--allow-unreviewed", *args)
    assert result.exit_code == 2
    assert json.loads(result.stdout)["status"] == "invalid"
    assert not output.exists()


def test_corrupt_dataset_keeps_cli_output_machine_readable(evaluation_root, tmp_path):
    (evaluation_root / "manifest.json").write_text("invalid JSON")
    result = invoke(evaluation_root, tmp_path / "unused", "--allow-unreviewed")
    assert result.exit_code == 2
    assert json.loads(result.stdout)["status"] == "invalid"


def test_existing_run_is_preserved(evaluation_root, tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    sentinel = output / "report.json"
    sentinel.write_text("original")
    result = invoke(evaluation_root, output, "--allow-unreviewed")
    assert result.exit_code == 2
    assert "new directory" in json.loads(result.stdout)["error"]
    assert sentinel.read_text() == "original"


def test_readable_cli_prints_result_paths(evaluation_root, tmp_path):
    output = tmp_path / "readable"
    result = runner.invoke(
        app,
        [
            "evaluate",
            "--dataset",
            str(evaluation_root),
            "--output",
            str(output),
            "--allow-unreviewed",
        ],
    )
    assert result.exit_code == 1
    assert "report.json" in result.stdout
    assert "report.md" in result.stdout
