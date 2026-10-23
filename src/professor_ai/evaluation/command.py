"""Composition layer for the development evaluation CLI."""

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import typer

from professor_ai.evaluation.fixtures import load_dataset
from professor_ai.evaluation.providers import AbstainingProvider, ReplayProvider
from professor_ai.evaluation.reporting import write_report
from professor_ai.evaluation.runner import EvaluationProvider, run_evaluation


def _revision() -> tuple[str, bool | None]:
    root = Path(__file__).resolve().parents[3]
    try:
        revision = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout
        return revision, bool(dirty)
    except (OSError, subprocess.SubprocessError):
        return "unknown", None


def evaluate(
    dataset: Annotated[Path, typer.Option(help="Versioned fixture dataset directory.")] = Path(
        "evals"
    ),
    provider: Annotated[
        str, typer.Option(help="Synthetic provider: abstain or replay.")
    ] = "abstain",
    responses: Annotated[Path | None, typer.Option(help="Dataset-bound replay JSON file.")] = None,
    output: Annotated[
        Path | None, typer.Option(help="New report directory outside the dataset.")
    ] = None,
    allow_unreviewed: Annotated[
        bool, typer.Option(help="Allow unreviewed proposals for development only.")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Print a JSON command summary.")
    ] = False,
) -> None:
    """Run offline pipeline diagnostics and write report.json plus report.md."""
    try:
        if provider not in {"abstain", "replay"}:
            raise ValueError("provider must be abstain or replay")
        if (provider == "replay") != (responses is not None):
            raise ValueError("--responses is required for replay and is only valid with replay")
        bundle = load_dataset(dataset)
        selected: EvaluationProvider = (
            ReplayProvider(
                responses,
                dataset_fingerprint=bundle.fingerprint,
                case_ids={case.id for case in bundle.cases},
            )
            if responses is not None
            else AbstainingProvider()
        )
        revision, dirty = _revision()
        report = run_evaluation(
            dataset,
            selected,
            allow_unreviewed=allow_unreviewed,
            project_revision=revision,
            working_tree_dirty=dirty,
        )
        if report.metadata.unreviewed_case_ids:
            typer.echo(
                "WARNING: unreviewed proposals allowed for development; not a benchmark.", err=True
            )
        if output is None:
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            output = Path("artifacts/evaluations") / f"{stamp}-{uuid4().hex[:8]}"
        write_report(report, output, dataset_root=dataset)
        failed = (
            report.summary.errors > 0
            or report.summary.status_matches.numerator != report.summary.total
        )
        summary = {
            "status": "completed_with_failures" if failed else "completed",
            "case_count": report.summary.total,
            "error_count": report.summary.errors,
            "status_match_count": report.summary.status_matches.numerator,
            "human_review_pending": bool(report.metadata.unreviewed_case_ids),
            "json_report": str(output.resolve() / "report.json"),
            "markdown_report": str(output.resolve() / "report.md"),
        }
    except (OSError, ValueError, RuntimeError) as error:
        if json_output:
            typer.echo(json.dumps({"status": "invalid", "error": str(error)[:2000]}))
        else:
            typer.echo(f"Evaluation could not run: {error}", err=True)
        raise typer.Exit(code=2) from None
    if json_output:
        typer.echo(json.dumps(summary))
    else:
        typer.echo(
            f"{summary['status']}: {report.summary.total} cases, "
            f"{report.summary.errors} stage errors"
        )
        typer.echo(f"JSON: {summary['json_report']}\nMarkdown: {summary['markdown_report']}")
    raise typer.Exit(code=1 if failed else 0)
