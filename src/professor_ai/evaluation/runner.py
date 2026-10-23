"""Execute offline provider stages without exposing grading annotations."""

import hashlib
import json
import platform
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Protocol
from uuid import uuid4

from pydantic import TypeAdapter

from professor_ai import __version__
from professor_ai.evaluation.fixtures import dataset_path, load_dataset
from professor_ai.evaluation.models import Case, Text
from professor_ai.evaluation.run_models import (
    Aggregate,
    CaseResult,
    EvaluationRequest,
    Evidence,
    Metric,
    ProviderAnswer,
    RunMetadata,
    RunReport,
    StageError,
    Timings,
)


class EvaluationProvider(Protocol):
    name: str
    fingerprint: str

    def retrieve(self, request: EvaluationRequest, sources: tuple[Evidence, ...]) -> object: ...
    def generate(self, request: EvaluationRequest, evidence: tuple[Evidence, ...]) -> object: ...


def fingerprint(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _execute(case: Case, sources: tuple[Evidence, ...], provider: EvaluationProvider) -> CaseResult:
    start = perf_counter()
    request = EvaluationRequest(
        id=case.id,
        question=case.question,
        language=case.language,
        selected_collections=tuple(case.selected_collections),
    )
    result = CaseResult(
        case_id=case.id,
        language=case.language,
        subject=case.subject,
        question=case.question,
        expected_status=case.expected_status,
        reference_answer=case.reference_answer,
        rubric=case.rubric,
        required_evidence_ids=case.required_evidence_ids,
        timings=Timings(),
    )
    stage: str = "retrieval"
    stage_start = perf_counter()
    try:
        ids = TypeAdapter(list[Text]).validate_python(
            provider.retrieve(request, sources), strict=True
        )
        available = {source.id: source for source in sources}
        if len(ids) != len(set(ids)) or not set(ids).issubset(available):
            raise ValueError("retrieved evidence is duplicate, unknown, or outside selected scope")
        result.selected_evidence_ids = ids
        selected = tuple(available[item] for item in ids)
        result.timings.retrieval_ms = (perf_counter() - stage_start) * 1000
        stage = "generation"
        stage_start = perf_counter()
        result.answer = ProviderAnswer.model_validate(provider.generate(request, selected))
        citations = result.answer.citations
        if len(citations) != len(set(citations)) or not set(citations).issubset(ids):
            raise ValueError("citations must resolve to distinct supplied evidence IDs")
        result.status_matches = result.answer.status == case.expected_status
    except Exception as error:
        result.error = StageError(
            stage="retrieval" if stage == "retrieval" else "generation",
            kind=type(error).__name__,
            message=str(error)[:1000],
        )
    finally:
        duration = (perf_counter() - stage_start) * 1000
        if stage == "retrieval":
            result.timings.retrieval_ms = duration
        else:
            result.timings.generation_ms = duration
        result.timings.total_ms = (perf_counter() - start) * 1000
    return result


def _metric(numerator: float, denominator: int) -> Metric:
    return Metric(
        numerator=numerator,
        denominator=denominator,
        value=numerator / denominator if denominator else None,
    )


def _aggregate(results: list[CaseResult]) -> Aggregate:
    needed = [r for r in results if r.required_evidence_ids]
    recall_sum = sum(
        len(set(r.required_evidence_ids) & set(r.selected_evidence_ids))
        / len(r.required_evidence_ids)
        for r in needed
    )
    return Aggregate(
        total=len(results),
        errors=sum(r.error is not None for r in results),
        status_matches=_metric(sum(r.status_matches for r in results), len(results)),
        evidence_recall=_metric(recall_sum, len(needed)),
    )


def run_evaluation(
    root: Path,
    provider: EvaluationProvider,
    *,
    allow_unreviewed: bool = False,
    project_revision: str = "unknown",
    working_tree_dirty: bool | None = None,
) -> RunReport:
    bundle = load_dataset(root)
    pending = [c.id for c in bundle.cases if c.review.status != "approved"]
    if pending and not allow_unreviewed:
        raise ValueError(
            "dataset requires human review; use --allow-unreviewed for development only"
        )
    started_at = datetime.now(UTC)
    config = {
        "dataset_fingerprint": bundle.fingerprint,
        "provider": provider.name,
        "provider_fingerprint": provider.fingerprint,
        "allow_unreviewed": allow_unreviewed,
        "project_revision": project_revision,
        "working_tree_dirty": working_tree_dirty,
        "package_version": __version__,
    }
    sources = []
    for doc in bundle.manifest.documents:
        content = dataset_path(root.resolve(), doc.path, "corpus").read_bytes()
        if hashlib.sha256(content).hexdigest() != doc.sha256:
            raise ValueError(f"source hash changed before execution: {doc.id}")
        sources.append(
            Evidence(
                id=doc.id,
                collection=doc.collection,
                language=doc.language,
                subject=doc.subject,
                text=content.decode("utf-8"),
            )
        )
    results = [
        _execute(
            case,
            tuple(
                s
                for s in sources
                if s.collection in case.selected_collections
                and s.language == case.language
                and s.subject == case.subject
            ),
            provider,
        )
        for case in bundle.cases
    ]
    languages: dict[str, list[CaseResult]] = defaultdict(list)
    subjects: dict[str, list[CaseResult]] = defaultdict(list)
    for result in results:
        languages[result.language].append(result)
        subjects[result.subject].append(result)
    return RunReport(
        metadata=RunMetadata(
            run_id=str(uuid4()),
            started_at=started_at,
            dataset_id=bundle.manifest.dataset_id,
            dataset_fingerprint=bundle.fingerprint,
            provider=provider.name,
            provider_fingerprint=provider.fingerprint,
            configuration_fingerprint=fingerprint(config),
            project_revision=project_revision,
            working_tree_dirty=working_tree_dirty,
            package_version=__version__,
            python_version=platform.python_version(),
            platform=platform.platform(),
            unreviewed_case_ids=pending,
            allow_unreviewed=allow_unreviewed,
        ),
        summary=_aggregate(results),
        by_language={k: _aggregate(v) for k, v in languages.items()},
        by_subject={k: _aggregate(v) for k, v in subjects.items()},
        results=results,
    )
