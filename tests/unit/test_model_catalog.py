import json

import pytest
from pydantic import ValidationError

from professor_ai.model_artifacts.catalog import (
    Artifact,
    Catalog,
    artifact_fingerprint,
    find_artifact,
    load_catalog,
)


def test_catalog_pins_four_candidates_and_declares_qualification_limits():
    catalog = load_catalog()
    assert len(catalog.artifacts) == 4
    assert sum(a.role == "generator" for a in catalog.artifacts) == 3
    assert sum(a.role == "embedding" for a in catalog.artifacts) == 1
    for artifact in catalog.artifacts:
        assert artifact.verification == "publisher_metadata_only"
        assert artifact.runtime.compatibility == "not_tested"
        assert any(f.purpose == "notice" for f in artifact.files)
        assert all(len(f.sha256) == 64 for f in artifact.files)
    e5 = find_artifact(catalog, "multilingual-e5-small")
    assert e5.configuration["dimension"] == 384
    assert e5.configuration["query_prefix"] == "query: "
    assert e5.configuration["passage_prefix"] == "passage: "


@pytest.mark.parametrize("revision", ["main", "v1", "a" * 39, "a/../b"])
def test_repository_revisions_must_be_immutable(artifact_payload, revision):
    artifact_payload["upstream"]["revision"] = revision
    with pytest.raises(ValidationError):
        Artifact.model_validate(artifact_payload)


@pytest.mark.parametrize(
    "path", ["../escape", "/tmp/escape", "a/../../escape", "a\\b", ".receipt.json"]
)
def test_managed_destinations_are_safe_relative_paths(artifact_payload, path):
    artifact_payload["files"][0]["destination"] = path
    with pytest.raises(ValidationError):
        Artifact.model_validate(artifact_payload)


def test_paths_cannot_alias_files_as_directories(artifact_payload):
    artifact_payload["files"][1]["destination"] = "weights.gguf/LICENSE"
    with pytest.raises(ValidationError, match="collision"):
        Artifact.model_validate(artifact_payload)


def test_duplicate_files_and_artifacts_are_rejected(artifact_payload):
    artifact_payload["files"].append(artifact_payload["files"][0])
    with pytest.raises(ValidationError, match="duplicate"):
        Artifact.model_validate(artifact_payload)
    artifact_payload["files"].pop()
    with pytest.raises(ValidationError, match="duplicate"):
        Catalog.model_validate(
            {
                "schema_version": 1,
                "checked_on": "2026-10-23",
                "artifacts": [artifact_payload, artifact_payload],
            }
        )


def test_fingerprint_covers_file_identity_and_settings(artifact_payload):
    first = artifact_fingerprint(Artifact.model_validate(artifact_payload))
    artifact_payload["configuration"]["context_tokens"] = 4096
    assert artifact_fingerprint(Artifact.model_validate(artifact_payload)) != first
    assert len(first) == 64


def test_unknown_model_id_is_actionable(artifact_catalog_path):
    with pytest.raises(ValueError, match="unknown artifact"):
        find_artifact(load_catalog(artifact_catalog_path), "missing")


@pytest.mark.parametrize(
    "field,value", [("sha256", "fake"), ("size_bytes", 0), ("size_bytes", True)]
)
def test_file_integrity_metadata_is_required(artifact_payload, field, value):
    artifact_payload["files"][0][field] = value
    with pytest.raises(ValidationError):
        Artifact.model_validate(artifact_payload)


def test_local_catalog_rejects_unknown_schema(artifact_catalog_path):
    data = json.loads(artifact_catalog_path.read_text())
    data["schema_version"] = 2
    artifact_catalog_path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_catalog(artifact_catalog_path)
