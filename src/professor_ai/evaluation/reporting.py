"""Readable diagnostics and new-directory-only JSON/Markdown artifacts."""

import re
from contextlib import suppress
from pathlib import Path

from professor_ai.evaluation.run_models import Aggregate, Metric, RunReport


def _block(text: str) -> str:
    # Provider text stays literal, even when it contains Markdown or code fences.
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", text)), default=0))
    return f"{fence}\n{text}\n{fence}"


def _value(metric: Metric) -> str:
    fraction = f"{metric.numerator:g}/{metric.denominator}"
    return fraction + (
        f" ({metric.value:.3f})" if metric.value is not None else " (not applicable)"
    )


def _summary(label: str, aggregate: Aggregate) -> list[str]:
    return [
        f"### {label}",
        "",
        f"Cases: {aggregate.total}; stage errors: {aggregate.errors}.",
        "Status agreement: " + _value(aggregate.status_matches),
        "",
        "Evidence recall: " + _value(aggregate.evidence_recall),
        "",
    ]


def render_report(report: RunReport) -> str:
    lines = [
        "# Development evaluation report",
        "",
        "Purpose: development_harness. Benchmark qualified: false.",
        "",
        "Synthetic provider diagnostics do not establish model quality or performance.",
        "",
        "Correctness: ungraded. Citation support: ungraded. Citation coverage: ungraded.",
        "",
        "Status agreement only compares status labels. Evidence recall measures returned IDs,",
        "not semantic answer correctness, citation support, ranking, or release recall@6.",
        "",
        "## Reproducibility",
        "",
        _block(report.metadata.model_dump_json(indent=2)),
        "",
    ]
    if report.metadata.unreviewed_case_ids:
        lines += ["WARNING: unreviewed proposals were explicitly allowed for development.", ""]
    lines += _summary("Overall", report.summary)
    for label, aggregate in report.by_language.items():
        lines += _summary("Language: " + label, aggregate)
    for label, aggregate in report.by_subject.items():
        lines += _summary("Subject: " + label, aggregate)
    lines += ["## Cases", ""]
    for index, result in enumerate(report.results, 1):
        lines += [f"### Case {index}", "", _block(result.model_dump_json(indent=2)), ""]
    return "\n".join(lines)


def write_report(report: RunReport, output: Path, *, dataset_root: Path) -> None:
    destination = output.resolve()
    if destination.is_relative_to(dataset_root.resolve()):
        raise ValueError("report output must be outside the dataset")
    if output.is_symlink() or destination.exists():
        raise ValueError("report output must be a new directory; existing outputs are preserved")
    json_text = report.model_dump_json(indent=2) + "\n"
    markdown = render_report(report)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()  # Atomically reserve a new run; never truncate an existing output.
    created: list[Path] = []
    try:
        for name, text in (("report.json", json_text), ("report.md", markdown)):
            path = destination / name
            with path.open("x", encoding="utf-8") as stream:
                created.append(path)
                stream.write(text)
    except OSError:
        for path in created:
            with suppress(OSError):
                path.unlink()
        with suppress(OSError):
            destination.rmdir()
        raise
