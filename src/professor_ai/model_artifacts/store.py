"""Immutable local snapshots, cooperative locking, and read-only byte verification."""

import json
import os
import shutil
import stat
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


def _verify_receipt(path: Path, artifact: Artifact) -> None:
    with path.open("rb") as stream:
        content = stream.read(4097)
    if len(content) > 4096:
        raise ArtifactStoreError("artifact receipt exceeds size limit")
    try:
        matches = json.loads(content) == _receipt(artifact)
    except (ValueError, RecursionError):
        raise ArtifactStoreError("artifact receipt is not valid JSON") from None
    if not matches:
        raise ArtifactStoreError("artifact receipt does not match catalog identity")


def _verify_inventory(root: Path, artifact: Artifact) -> None:
    expected_files = {Path(file.destination) for file in artifact.files} | {Path(RECEIPT)}
    expected_dirs = {parent for file in expected_files for parent in file.parents}
    pending = [root]
    while pending:
        for entry in pending.pop().iterdir():
            relative = entry.relative_to(root)
            mode = entry.lstat().st_mode
            if relative in expected_dirs and stat.S_ISDIR(mode):
                pending.append(entry)
            elif relative not in expected_files or not stat.S_ISREG(mode):
                raise ArtifactStoreError(f"unlisted or non-regular artifact entry: {relative}")


def verify_artifact(artifact: Artifact, root: Path) -> InstallReport:
    artifact = Artifact.model_validate(artifact)
    path = root.resolve() / artifact.id / artifact_fingerprint(artifact)
    verified = 0
    size = 0
    try:
        path = installation_path(artifact, root)
        if not path.exists():
            return InstallReport(artifact_id=artifact.id, path=str(path), status="missing")
        _verify_inventory(path, artifact)
        for file in artifact.files:
            verify_file(_path(path, file.destination), file)
            verified += 1
            size += file.size_bytes
        receipt = _path(path, RECEIPT)
        _verify_receipt(receipt, artifact)
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
            _verify_receipt(receipt, artifact)
        else:
            with receipt.open("x", encoding="utf-8") as stream:
                json.dump(_receipt(artifact), stream, sort_keys=True)
        _verify_inventory(staging, artifact)
        destination = installation_path(artifact, root)
        destination.parent.mkdir(exist_ok=True)
        if destination.exists():
            raise ArtifactStoreError("installation appeared during download; preserved")
        staging.rename(destination)
        return verify_artifact(artifact, root)
    finally:
        lock.unlink(missing_ok=True)
