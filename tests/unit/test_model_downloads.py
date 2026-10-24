from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from professor_ai.model_artifacts.catalog import artifact_fingerprint, find_artifact, load_catalog
from professor_ai.model_artifacts.store import ArtifactStoreError, fetch_artifact, verify_artifact

BLOBS = {"weights.gguf": b"tiny-model-bytes", "LICENSE": b"Test fixture notice\n"}


def candidate(path):
    return find_artifact(load_catalog(path), "tiny-model")


def response(request):
    return httpx.Response(200, content=BLOBS[request.url.path.split("/")[-1]])


class InterruptedStream(httpx.SyncByteStream):
    def __iter__(self):
        yield b"tiny-"
        raise httpx.ReadError("simulated interruption")


def interrupt(artifact, root):
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, stream=InterruptedStream())
        )
    ) as client:
        with pytest.raises(ArtifactStoreError):
            fetch_artifact(artifact, root, client=client)
    assert verify_artifact(artifact, root).status == "missing"


def test_all_files_are_verified_before_publication_and_refetch_is_offline(
    artifact_catalog_path, tmp_path
):
    artifact = candidate(artifact_catalog_path)
    root = tmp_path / "models"
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        report = fetch_artifact(artifact, root, client=client)
    assert report.status == "verified"
    assert report.files_verified == 2
    assert report.bytes_verified == sum(map(len, BLOBS.values()))
    assert report.runtime_qualified is False
    assert (Path(report.path) / "LICENSE").read_bytes() == BLOBS["LICENSE"]
    # Any accidental network request is blocked by pytest-socket.
    assert fetch_artifact(artifact, root).status == "verified"
    assert verify_artifact(artifact, root).status == "verified"


@pytest.mark.parametrize("ignore_range", [False, True])
def test_interrupted_transfer_resumes_or_safely_restarts(
    artifact_catalog_path, tmp_path, ignore_range
):
    artifact = candidate(artifact_catalog_path)
    root = tmp_path / "models"
    interrupt(artifact, root)
    seen = []

    def handler(request):
        if request.url.path.endswith("weights.gguf"):
            seen.append(request.headers.get("range"))
            if not ignore_range:
                blob = BLOBS["weights.gguf"]
                return httpx.Response(
                    206,
                    content=blob[5:],
                    headers={"Content-Range": f"bytes 5-{len(blob) - 1}/{len(blob)}"},
                )
        return response(request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        report = fetch_artifact(artifact, root, client=client)
    assert report.status == "verified"
    assert seen == ["bytes=5-"]
    assert (Path(report.path) / "weights.gguf").read_bytes() == BLOBS["weights.gguf"]


@pytest.mark.parametrize(
    "mode", ["wrong_range", "wrong_total", "short", "oversize", "hash", "encoding"]
)
def test_invalid_server_data_never_becomes_an_installation(artifact_catalog_path, tmp_path, mode):
    artifact = candidate(artifact_catalog_path)
    root = tmp_path / "models"
    if mode.startswith("wrong"):
        interrupt(artifact, root)

    def handler(request):
        blob = BLOBS["weights.gguf"]
        if mode == "wrong_range":
            return httpx.Response(206, content=blob[5:], headers={"Content-Range": "bytes 0-9/15"})
        if mode == "wrong_total":
            return httpx.Response(
                206, content=blob[5:], headers={"Content-Range": "bytes 5-14/999"}
            )
        if mode == "short":
            return httpx.Response(200, content=blob[:3], headers={"Content-Length": str(len(blob))})
        if mode == "oversize":
            return httpx.Response(200, content=blob + b"extra")
        if mode == "encoding":
            return httpx.Response(200, content=blob, headers={"Content-Encoding": "gzip"})
        return httpx.Response(200, content=b"x" * len(blob))

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ArtifactStoreError):
            fetch_artifact(artifact, root, client=client)
    assert verify_artifact(artifact, root).status == "missing"


def test_redirects_require_https_before_the_redirected_request(artifact_catalog_path, tmp_path):
    artifact = candidate(artifact_catalog_path)
    seen = []

    def redirect(request):
        seen.append(str(request.url))
        return httpx.Response(302, headers={"Location": "http://insecure.invalid/weights"})

    with httpx.Client(transport=httpx.MockTransport(redirect), follow_redirects=True) as client:
        with pytest.raises(ArtifactStoreError, match="HTTPS"):
            fetch_artifact(artifact, tmp_path / "models", client=client)
    assert len(seen) == 1


def test_https_cdn_redirect_can_complete(artifact_catalog_path, tmp_path):
    def handler(request):
        if request.url.host == "huggingface.co":
            return httpx.Response(
                307, headers={"Location": "https://cdn.example/" + request.url.path.split("/")[-1]}
            )
        return response(request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert (
            fetch_artifact(
                candidate(artifact_catalog_path), tmp_path / "models", client=client
            ).status
            == "verified"
        )


def test_insufficient_disk_is_detected_before_network_or_installation(
    artifact_catalog_path, tmp_path, monkeypatch
):
    root = tmp_path / "models"
    monkeypatch.setattr(
        "professor_ai.model_artifacts.store.shutil.disk_usage", lambda path: SimpleNamespace(free=0)
    )
    with pytest.raises(ArtifactStoreError, match="disk"):
        fetch_artifact(candidate(artifact_catalog_path), root)
    assert not root.exists()


def test_concurrent_fetch_is_rejected(artifact_catalog_path, tmp_path):
    artifact = candidate(artifact_catalog_path)
    root = tmp_path / "models"
    checked = []

    def handler(request):
        with pytest.raises(ArtifactStoreError, match="lock"):
            fetch_artifact(artifact, root)
        checked.append(True)
        return response(request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert fetch_artifact(artifact, root, client=client).status == "verified"
    assert checked


def test_existing_corrupt_installation_is_preserved(artifact_catalog_path, tmp_path):
    artifact = candidate(artifact_catalog_path)
    root = tmp_path / "models"
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        installed = fetch_artifact(artifact, root, client=client)
    weight = Path(installed.path) / "weights.gguf"
    weight.write_bytes(b"changed")
    assert verify_artifact(artifact, root).status == "invalid"
    with pytest.raises(ArtifactStoreError, match="invalid"):
        fetch_artifact(artifact, root)
    assert weight.read_bytes() == b"changed"


def test_symlinked_managed_parent_cannot_write_outside_store(artifact_catalog_path, tmp_path):
    root = tmp_path / "models"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / ".downloads").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ArtifactStoreError, match="symlink"):
        fetch_artifact(candidate(artifact_catalog_path), root)
    assert not list(outside.iterdir())


def test_verify_missing_store_is_read_only(artifact_catalog_path, tmp_path):
    root = tmp_path / "absent"
    report = verify_artifact(candidate(artifact_catalog_path), root)
    assert report.status == "missing"
    assert not root.exists()


def test_hardlinked_partial_cannot_modify_an_external_file(artifact_catalog_path, tmp_path):
    artifact = candidate(artifact_catalog_path)
    root = tmp_path / "models"
    interrupt(artifact, root)
    partial = next(root.rglob("*.part"))
    outside = tmp_path / "outside"
    outside.write_bytes(partial.read_bytes())
    partial.unlink()
    partial.hardlink_to(outside)
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        with pytest.raises(ArtifactStoreError, match="hardlink"):
            fetch_artifact(artifact, root, client=client)
    assert outside.read_bytes() == b"tiny-"
    assert verify_artifact(artifact, root).status == "missing"


@pytest.mark.parametrize("extra_kind", ["file", "symlink"])
def test_unlisted_staged_entries_are_not_published(artifact_catalog_path, tmp_path, extra_kind):
    artifact = candidate(artifact_catalog_path)
    root = tmp_path / "models"
    interrupt(artifact, root)
    staging = root / ".downloads" / f"{artifact.id}-{artifact_fingerprint(artifact)}"
    extra = staging / "unlisted"
    if extra_kind == "symlink":
        extra.symlink_to(tmp_path / "absent")
    else:
        extra.write_bytes(b"unexpected")
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        with pytest.raises(ArtifactStoreError, match="unlisted"):
            fetch_artifact(artifact, root, client=client)
    assert extra.exists() or extra.is_symlink()
    assert verify_artifact(artifact, root).status == "missing"


def test_verify_rejects_unlisted_installed_entries(artifact_catalog_path, tmp_path):
    artifact = candidate(artifact_catalog_path)
    root = tmp_path / "models"
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        report = fetch_artifact(artifact, root, client=client)
    extra = Path(report.path) / "unlisted"
    extra.write_bytes(b"unexpected")
    checked = verify_artifact(artifact, root)
    assert checked.status == "invalid"
    assert "unlisted" in checked.errors[0]
    assert extra.read_bytes() == b"unexpected"
