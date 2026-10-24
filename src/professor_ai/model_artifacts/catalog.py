"""Immutable publisher references and safe artifact layout contracts."""

import hashlib
import json
import re
from datetime import date
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Annotated, Literal, Self
from urllib.parse import quote

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    JsonValue,
    StringConstraints,
    field_validator,
    model_validator,
)

Digest = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
Revision = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{40}$")]
Identifier = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9._-]{0,79}$")]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, revalidate_instances="always")


class Repository(Record):
    repository: Annotated[
        str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*$")
    ]
    revision: Revision


def safe_relative(value: str) -> str:
    parts = value.split("/")
    if not all(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", part) for part in parts):
        raise ValueError("artifact paths require safe relative filename components")
    return value


class RemoteFile(Record):
    source: Repository
    path: str
    destination: str
    size_bytes: int = Field(gt=0, strict=True)
    sha256: Digest
    purpose: Literal["weights", "notice", "configuration"]

    _paths = field_validator("path", "destination")(safe_relative)

    @property
    def url(self) -> str:
        return (
            f"https://huggingface.co/{self.source.repository}/resolve/"
            f"{self.source.revision}/{quote(self.path, safe='/')}"
        )


class RuntimeReference(Record):
    name: str
    version: str
    revision: Revision | None
    compatibility: Literal["not_tested"]


class Artifact(Record):
    id: Identifier
    role: Literal["generator", "embedding"]
    upstream: Repository
    distribution: Repository
    license: Literal["MIT", "Apache-2.0"]
    license_evidence: list[HttpUrl] = Field(min_length=1)
    provenance: str = Field(min_length=1)
    source_revision_relation: Literal["direct", "publisher_declared_base_only"]
    verification: Literal["publisher_metadata_only"]
    runtime: RuntimeReference
    configuration: dict[str, JsonValue]
    files: list[RemoteFile] = Field(min_length=1)

    @model_validator(mode="after")
    def layout_and_purposes(self) -> Self:
        paths = [PurePosixPath(f.destination.casefold()) for f in self.files]
        if len(paths) != len(set(paths)):
            raise ValueError("duplicate artifact destinations")
        if any(a in b.parents for a in paths for b in paths if a != b):
            raise ValueError("artifact file/directory collision")
        spellings: dict[str, str] = {}
        for file in self.files:
            path = PurePosixPath(file.destination)
            for component in (path, *path.parents):
                name = str(component)
                previous = spellings.setdefault(name.casefold(), name)
                if previous != name:
                    raise ValueError("artifact path case collision")
        purposes = {f.purpose for f in self.files}
        if not {"weights", "notice"}.issubset(purposes):
            raise ValueError("artifacts need weights and notice/license evidence files")
        if any(url.scheme != "https" for url in self.license_evidence):
            raise ValueError("license evidence requires HTTPS")
        return self


class Catalog(Record):
    schema_version: Literal[1]
    checked_on: date
    artifacts: list[Artifact] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self) -> Self:
        if len(self.artifacts) != len({a.id for a in self.artifacts}):
            raise ValueError("duplicate artifact IDs")
        return self


def artifact_fingerprint(artifact: Artifact) -> str:
    value = json.dumps(artifact.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(value.encode()).hexdigest()


def load_catalog(path: Path | None = None) -> Catalog:
    content = (
        path.read_bytes() if path else files(__package__).joinpath("catalog.json").read_bytes()
    )
    return Catalog.model_validate_json(content)


def find_artifact(catalog: Catalog, artifact_id: str) -> Artifact:
    for artifact in catalog.artifacts:
        if artifact.id == artifact_id:
            return artifact
    raise ValueError(f"unknown artifact {artifact_id!r}; use 'models list' to see candidates")
