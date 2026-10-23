import json

import httpx
import pytest
from typer.testing import CliRunner

from professor_ai.cli import app
from professor_ai.model_artifacts.store import fetch_artifact

runner = CliRunner()


def test_bundled_catalog_can_be_listed_and_inspected_without_network_or_writes(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    listed = runner.invoke(app, ["models", "list", "--json"])
    assert listed.exit_code == 0, listed.output
    assert len(json.loads(listed.stdout)["artifacts"]) == 4
    inspected = runner.invoke(app, ["models", "inspect", "qwen3.5-4b-q4_k_m", "--json"])
    assert inspected.exit_code == 0
    data = json.loads(inspected.stdout)
    assert data["runtime_qualified"] is False
    assert len(data["fingerprint"]) == 64
    assert list(tmp_path.iterdir()) == []


def test_verify_missing_models_is_read_only(artifact_catalog_path, tmp_path):
    root = tmp_path / "missing"
    result = runner.invoke(
        app,
        [
            "models",
            "verify",
            "tiny-model",
            "--catalog",
            str(artifact_catalog_path),
            "--directory",
            str(root),
            "--json",
        ],
    )
    assert result.exit_code == 1
    assert json.loads(result.stdout)["status"] == "missing"
    assert not root.exists()


def test_explicit_fetch_verifies_a_tiny_fixture_through_a_local_transport(
    artifact_catalog_path, tmp_path, monkeypatch
):
    blobs = {"weights.gguf": b"tiny-model-bytes", "LICENSE": b"Test fixture notice\n"}

    def local_fetch(artifact, root):
        with httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, content=blobs[request.url.path.split("/")[-1]])
            )
        ) as client:
            return fetch_artifact(artifact, root, client=client)

    monkeypatch.setattr("professor_ai.model_artifacts.command.fetch_artifact", local_fetch)
    root = tmp_path / "store"
    result = runner.invoke(
        app,
        [
            "models",
            "fetch",
            "tiny-model",
            "--catalog",
            str(artifact_catalog_path),
            "--directory",
            str(root),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert data["status"] == "verified" and data["files_verified"] == 2
    assert data["runtime_qualified"] is False
    checked = runner.invoke(
        app,
        [
            "models",
            "verify",
            "tiny-model",
            "--catalog",
            str(artifact_catalog_path),
            "--directory",
            str(root),
            "--json",
        ],
    )
    assert checked.exit_code == 0
    doctor = runner.invoke(app, ["doctor", "--json"])
    assert any(
        c["name"] == "model" and c["status"] == "missing"
        for c in json.loads(doctor.stdout)["checks"]
    )


@pytest.mark.parametrize("command", ["inspect", "verify", "fetch"])
def test_unknown_model_returns_a_json_configuration_error(command):
    result = runner.invoke(app, ["models", command, "unknown", "--json"])
    assert result.exit_code == 2
    assert json.loads(result.stdout)["status"] == "invalid"
    assert "unknown artifact" in json.loads(result.stdout)["error"]


def test_corrupt_catalog_is_a_json_error(artifact_catalog_path):
    artifact_catalog_path.write_text("not JSON")
    result = runner.invoke(
        app, ["models", "list", "--catalog", str(artifact_catalog_path), "--json"]
    )
    assert result.exit_code == 2
    assert json.loads(result.stdout)["status"] == "invalid"


def test_transfer_failure_keeps_machine_readable_output(
    artifact_catalog_path, tmp_path, monkeypatch
):
    from professor_ai.model_artifacts.store import ArtifactStoreError

    def fail(artifact, root):
        raise ArtifactStoreError("interrupted; retry to resume")

    monkeypatch.setattr("professor_ai.model_artifacts.command.fetch_artifact", fail)
    result = runner.invoke(
        app,
        [
            "models",
            "fetch",
            "tiny-model",
            "--catalog",
            str(artifact_catalog_path),
            "--directory",
            str(tmp_path / "store"),
            "--json",
        ],
    )
    assert result.exit_code == 1
    assert json.loads(result.stdout)["status"] == "failed"
