"""Synthetic offline providers for exercising the harness, never for quality claims."""

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import JsonValue

from professor_ai.evaluation.models import Record
from professor_ai.evaluation.run_models import EvaluationRequest, Evidence
from professor_ai.evaluation.runner import fingerprint


class AbstainingProvider:
    name = "abstain"
    fingerprint = fingerprint({"provider": "abstain", "version": 1})

    def retrieve(self, request: EvaluationRequest, sources: tuple[Evidence, ...]) -> object:
        return []

    def generate(self, request: EvaluationRequest, evidence: tuple[Evidence, ...]) -> object:
        text = (
            "This baseline does not retrieve evidence or answer questions."
            if request.language == "en"
            else "Esta linha de base não recupera evidências nem responde a perguntas."
        )
        return {"status": "insufficient_evidence", "text": text, "citations": []}


class ReplayEntry(Record):
    evidence_ids: JsonValue
    answer: JsonValue


class ReplayFile(Record):
    schema_version: Literal[1]
    dataset_fingerprint: str
    results: dict[str, ReplayEntry]


class ReplayProvider:
    name = "replay"

    def __init__(self, path: Path, *, dataset_fingerprint: str, case_ids: set[str]) -> None:
        data = path.read_bytes()
        replay = ReplayFile.model_validate_json(data)
        if replay.dataset_fingerprint != dataset_fingerprint:
            raise ValueError("replay dataset fingerprint does not match the loaded dataset")
        unknown = replay.results.keys() - case_ids
        if unknown:
            raise ValueError("unknown replay case IDs: " + ", ".join(sorted(unknown)))
        self.fingerprint = hashlib.sha256(data).hexdigest()
        self.dataset_fingerprint = replay.dataset_fingerprint
        self._results = replay.results

    def retrieve(self, request: EvaluationRequest, sources: tuple[Evidence, ...]) -> object:
        if request.id not in self._results:
            raise ValueError(f"missing replay output for case: {request.id}")
        return self._results[request.id].evidence_ids

    def generate(self, request: EvaluationRequest, evidence: tuple[Evidence, ...]) -> object:
        return self._results[request.id].answer
