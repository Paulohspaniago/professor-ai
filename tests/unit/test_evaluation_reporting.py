import pytest

from professor_ai.evaluation.providers import AbstainingProvider
from professor_ai.evaluation.reporting import render_report, write_report
from professor_ai.evaluation.run_models import RunReport
from professor_ai.evaluation.runner import run_evaluation


def test_reports_roundtrip_and_show_raw_counts_and_ungraded_metrics(evaluation_root, tmp_path):
    report = run_evaluation(evaluation_root, AbstainingProvider(), allow_unreviewed=True)
    output = tmp_path / "new-run"
    write_report(report, output, dataset_root=evaluation_root)

    assert RunReport.model_validate_json((output / "report.json").read_bytes()) == report
    text = (output / "report.md").read_text()
    assert "0/2" in text
    assert "Correctness: ungraded" in text
    assert "development_harness" in text
    assert "smoke-math-01-en" in text


def test_report_includes_stage_errors_and_preserves_embedded_markdown(evaluation_root):
    class BrokenProvider(AbstainingProvider):
        def retrieve(self, request, sources):
            raise ValueError("```\n![untrusted](https://example.invalid/image)\n```")

    report = run_evaluation(evaluation_root, BrokenProvider(), allow_unreviewed=True)
    text = render_report(report)
    assert "retrieval" in text
    assert "ValueError" in text
    assert "````\n" in text
    assert "2/2" not in text.split("Status agreement:")[1].splitlines()[0]


def test_report_output_never_overwrites_an_existing_directory(evaluation_root, tmp_path):
    report = run_evaluation(evaluation_root, AbstainingProvider(), allow_unreviewed=True)
    output = tmp_path / "existing"
    output.mkdir()
    sentinel = output / "report.json"
    sentinel.write_text("preserve me")

    with pytest.raises((ValueError, FileExistsError)):
        write_report(report, output, dataset_root=evaluation_root)
    assert sentinel.read_text() == "preserve me"


@pytest.mark.parametrize("inside", ["run", "corpus/run", "cases/run"])
def test_report_cannot_be_written_inside_the_dataset(evaluation_root, inside):
    report = run_evaluation(evaluation_root, AbstainingProvider(), allow_unreviewed=True)
    with pytest.raises(ValueError, match="dataset"):
        write_report(report, evaluation_root / inside, dataset_root=evaluation_root)
    assert not (evaluation_root / inside).exists()


def test_symlink_parent_cannot_route_output_into_dataset(evaluation_root, tmp_path):
    report = run_evaluation(evaluation_root, AbstainingProvider(), allow_unreviewed=True)
    alias = tmp_path / "alias"
    alias.symlink_to(evaluation_root, target_is_directory=True)
    with pytest.raises(ValueError, match="dataset"):
        write_report(report, alias / "new-run", dataset_root=evaluation_root)
    assert not (evaluation_root / "new-run").exists()


def test_symlink_output_does_not_modify_its_target(evaluation_root, tmp_path):
    report = run_evaluation(evaluation_root, AbstainingProvider(), allow_unreviewed=True)
    target = tmp_path / "untouched"
    target.mkdir()
    output = tmp_path / "linked"
    output.symlink_to(target, target_is_directory=True)
    with pytest.raises((ValueError, FileExistsError)):
        write_report(report, output, dataset_root=evaluation_root)
    assert not list(target.iterdir())
