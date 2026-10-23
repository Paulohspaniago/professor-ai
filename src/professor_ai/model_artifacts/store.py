"""Immutable local snapshots, cooperative locking, and read-only byte verification."""

import json
import os
import shutil
from contextlib import nullcontext
from pathlib import Path
from typing import Literal

import httpx

from professor_ai.model_artifacts.catalog import Artifact, Record, artifact_fingerprint
from professor_ai.model_artifacts.transfer import ArtifactStoreError as ArtifactStoreError
from professor_ai.model_artifacts.transfer import transfer_file, verify_file

DISK_RESERVE_BYTES = 64 * 1024 * 1024
RECEIPT = ".receipt.json"


class InstallReport(Record):
    artifact_id: str
    path: str
    status: Literal["missing", "invalid", "verified"]
    files_verified: int = 0
    bytes_verified: int = 0
    runtime_qualified: Literal[False] = False
    errors: list[str] = []


def _path(root: Path, relative: str) -> Path:
    path = root
    for component in relative.split("/"):
        path = path / component
        if path.is_symlink():
            raise ArtifactStoreError(f"symlink in managed artifact path: {path}")
    return path


def installation_path(artifact: Artifact, root: Path) -> Path:
    return _path(root.resolve(), f"{artifact.id}/{artifact_fingerprint(artifact)}")


def _receipt(artifact: Artifact) -> dict[str, object]:
    return {
        "schema_version": 1,
        "artifact_id": artifact.id,
        "fingerprint": artifact_fingerprint(artifact),
    }


def verify_artifact(artifact: Artifact, root: Path) -> InstallReport:
    artifact = Artifact.model_validate(artifact)
    path = root.resolve() / artifact.id / artifact_fingerprint(artifact)
    verified = 0
    size = 0
    try:
        path = installation_path(artifact, root)
        if not path.exists():
            return InstallReport(artifact_id=artifact.id, path=str(path), status="missing")
        for file in artifact.files:
            verify_file(_path(path, file.destination), file)
            verified += 1
            size += file.size_bytes
        receipt = _path(path, RECEIPT)
        if receipt.stat().st_size > 4096 or json.loads(receipt.read_bytes()) != _receipt(artifact):
            raise ArtifactStoreError("artifact receipt does not match catalog identity")
        return InstallReport(
            artifact_id=artifact.id,
            path=str(path),
            status="verified",
            files_verified=verified,
            bytes_verified=size,
        )
    except (OSError, ValueError, RuntimeError) as error:
        return InstallReport(
            artifact_id=artifact.id,
            path=str(path),
            status="invalid",
            files_verified=verified,
            bytes_verified=size,
            errors=[str(error)],
        )


def fetch_artifact(
    artifact: Artifact,
    root: Path,
    *,
    client: httpx.Client | None = None,
) -> InstallReport:
    artifact = Artifact.model_validate(artifact)
    current = verify_artifact(artifact, root)
    if current.status == "verified":
        return current
    if current.status == "invalid":
        raise ArtifactStoreError(
            "invalid existing installation is preserved: " + "; ".join(current.errors)
        )
    root = root.resolve()
    identity = artifact_fingerprint(artifact)
    staging = _path(root, f".downloads/{artifact.id}-{identity}")
    remaining = 0
    for file in artifact.files:
        target = _path(staging, file.destination)
        partial = _path(staging, f".partials/{file.sha256}.part")
        present = (
            target.stat().st_size
            if target.exists()
            else (partial.stat().st_size if partial.exists() else 0)
        )
        if present > file.size_bytes:
            raise ArtifactStoreError("oversized managed partial; inspect it before retrying")
        remaining += file.size_bytes - present
    ancestor = root
    while not ancestor.exists():
        ancestor = ancestor.parent
    if not ancestor.is_dir():
        raise ArtifactStoreError("model store must be a directory")
    if shutil.disk_usage(ancestor).free < remaining + DISK_RESERVE_BYTES:
        raise ArtifactStoreError(
            f"insufficient disk space: need {remaining + DISK_RESERVE_BYTES} bytes"
        )
    downloads = _path(root, ".downloads")
    downloads.mkdir(parents=True, exist_ok=True)
    lock = _path(downloads, f"{artifact.id}-{identity}.lock")
    try:
        lock_file = lock.open("x", encoding="utf-8")
    except FileExistsError:
        raise ArtifactStoreError(f"artifact download lock exists: {lock}") from None
    try:
        with lock_file:
            lock_file.write(str(os.getpid()))
        staging.mkdir(exist_ok=True)
        partials = _path(staging, ".partials")
        partials.mkdir(exist_ok=True)
        manager = (
            nullcontext(client)
            if client is not None
            else httpx.Client(
                timeout=httpx.Timeout(60, connect=15),
                follow_redirects=False,
            )
        )
        with manager as transport:
            for file in artifact.files:
                target = _path(staging, file.destination)
                target.parent.mkdir(parents=True, exist_ok=True)
                partial = _path(partials, f"{file.sha256}.part")
                transfer_file(file, target, partial, transport)
        partials.rmdir()
        receipt = _path(staging, RECEIPT)
        if receipt.exists():
            if json.loads(receipt.read_bytes()) != _receipt(artifact):
                raise ArtifactStoreError("staged receipt identity mismatch")
        else:
            with receipt.open("x", encoding="utf-8") as stream:
                json.dump(_receipt(artifact), stream, sort_keys=True)
        destination = installation_path(artifact, root)
        destination.parent.mkdir(exist_ok=True)
        if destination.exists():
            raise ArtifactStoreError("installation appeared during download; preserved")
        staging.rename(destination)
        return verify_artifact(artifact, root)
    finally:
        lock.unlink(missing_ok=True)
