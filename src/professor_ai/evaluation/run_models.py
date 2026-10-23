"""Versioned development-run contracts, separate from provider-visible inputs."""

from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field

from professor_ai.evaluation.models import Language, Record, Rubric, Status, Subject, Text


class EvaluationRequest(Record):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: Text
    question: Text
    language: Language
    selected_collections: tuple[Text, ...]


class Evidence(Record):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: Text
    collection: Text
    language: Language
    subject: Subject
    text: Text


class ProviderAnswer(Record):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    status: Status
    text: Text
    citations: list[Text]


class StageError(Record):
    stage: Literal["retrieval", "generation"]
    kind: str
    message: str


class Timings(Record):
    retrieval_ms: float | None = None
    generation_ms: float | None = None
    total_ms: float = 0


class CaseResult(Record):
    case_id: str
    language: Language
    subject: Subject
    question: str
    expected_status: Status
    reference_answer: str
    rubric: Rubric
    required_evidence_ids: list[str]
    selected_evidence_ids: list[str] = Field(default_factory=list)
    answer: ProviderAnswer | None = None
    error: StageError | None = None
    timings: Timings
    status_matches: bool = False


class Metric(Record):
    numerator: float
    denominator: int
    value: float | None


class Aggregate(Record):
    total: int
    errors: int
    status_matches: Metric
    evidence_recall: Metric


class RunMetadata(Record):
    run_id: str
    started_at: datetime
    dataset_id: str
    dataset_fingerprint: str
    provider: str
    provider_fingerprint: str
    configuration_fingerprint: str
    project_revision: str
    working_tree_dirty: bool | None
    package_version: str
    python_version: str
    platform: str
    unreviewed_case_ids: list[str]
    allow_unreviewed: bool
    model_artifacts: list[str] = Field(default_factory=list)
    tokenizer: str | None = None
    prompt_version: str | None = None
    index_generation: str | None = None


class RunReport(Record):
    schema_version: Literal[1] = 1
    purpose: Literal["development_harness"] = "development_harness"
    benchmark_qualified: Literal[False] = False
    metadata: RunMetadata
    summary: Aggregate
    by_language: dict[str, Aggregate]
    by_subject: dict[str, Aggregate]
    human_metrics: dict[str, None] = Field(
        default_factory=lambda: {
            "correctness": None,
            "citation_support": None,
            "citation_coverage": None,
        }
    )
    results: list[CaseResult]
