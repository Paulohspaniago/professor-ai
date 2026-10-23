"""Versioned contracts for source material and evaluation annotations."""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Language = Literal["en", "pt-BR"]
Subject = Literal["computer_science", "mathematics", "physics"]
Status = Literal["answered", "insufficient_evidence", "conflicting_evidence"]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Reference(Record):
    title: Text
    url: HttpUrl
    checked_on: date


class Document(Record):
    id: Text
    collection: Text
    subject: Subject
    language: Language
    path: Text
    sha256: Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
    title: Text
    license: Literal["MIT"]
    authorship: Text
    kind: Literal["original_note", "fictional_record"]
    references: list[Reference]

    @model_validator(mode="after")
    def original_notes_have_references(self) -> Self:
        if self.kind == "original_note" and not self.references:
            raise ValueError("original notes require corroborating references")
        return self


class Counts(Record):
    cases: int = Field(gt=0)
    languages: dict[Language, int]
    subjects: dict[Subject, int]


class Manifest(Record):
    schema_version: Literal[1]
    dataset_id: Text
    split: Literal["smoke-development"]
    case_file: Text
    expected_counts: Counts
    documents: list[Document] = Field(min_length=1)


class Review(Record):
    status: Literal["pending_human_review", "approved", "changes_requested"]
    reviewer: Text | None
    reviewed_on: date | None
    notes: str

    @model_validator(mode="after")
    def require_attribution(self) -> Self:
        if self.status == "pending_human_review":
            if self.reviewer is not None or self.reviewed_on is not None:
                raise ValueError("pending review cannot record an approval attribution")
        elif self.reviewer is None or self.reviewed_on is None:
            raise ValueError("completed review requires reviewer and reviewed_on")
        return self


class NumericAnswer(Record):
    value: float = Field(allow_inf_nan=False)
    unit: Text
    tolerance: float = Field(ge=0, allow_inf_nan=False)


class Rubric(Record):
    must_include: list[Text] = Field(min_length=1)
    must_not_include: list[Text]


class Case(Record):
    id: Text
    family_id: Text
    language: Language
    subject: Subject
    category: Literal["conceptual", "derivation", "insufficient_evidence", "conflicting_evidence"]
    selected_collections: list[Text] = Field(min_length=1)
    question: Text
    expected_status: Status
    reference_answer: Text
    required_evidence_ids: list[Text]
    rubric: Rubric
    tags: list[Literal["multi_source"]]
    missing_information: list[Text]
    numeric_answer: NumericAnswer | None
    review: Review

    @model_validator(mode="after")
    def evidence_contract(self) -> Self:
        ids = self.required_evidence_ids
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate evidence IDs")
        if len(self.selected_collections) != len(set(self.selected_collections)):
            raise ValueError("duplicate selected collections")
        expected = self.category if self.category.endswith("evidence") else "answered"
        if self.expected_status != expected:
            raise ValueError("category and expected_status disagree")
        if expected == "insufficient_evidence":
            if ids or not self.missing_information or self.numeric_answer is not None:
                raise ValueError("insufficient evidence requires missing information and no target")
        elif not ids or self.missing_information:
            raise ValueError("answer/conflict needs evidence and no missing information")
        if (expected == "conflicting_evidence" or "multi_source" in self.tags) and len(ids) < 2:
            raise ValueError("conflict/multi_source needs two distinct evidence units")
        return self


class ValidationReport(Record):
    passed: bool
    status: Literal["valid_draft", "review_required", "human_reviewed", "invalid"]
    case_count: int = 0
    document_count: int = 0
    reviewed_case_count: int = 0
    unreviewed_case_ids: list[str] = Field(default_factory=list)
    fingerprint: str = ""
    errors: list[str] = Field(default_factory=list)
