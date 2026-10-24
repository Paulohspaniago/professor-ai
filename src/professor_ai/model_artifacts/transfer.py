"""Bounded HTTPS transfers into unpublished managed partial files."""

import hashlib
import re
from pathlib import Path

import httpx

from professor_ai.model_artifacts.catalog import RemoteFile


class ArtifactStoreError(RuntimeError):
    """An artifact could not be acquired or verified safely."""


def verify_file(path: Path, file: RemoteFile) -> None:
    if path.stat().st_size != file.size_bytes:
        raise ArtifactStoreError(f"size mismatch: {file.destination}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    if digest.hexdigest() != file.sha256:
        raise ArtifactStoreError(f"SHA-256 mismatch: {file.destination}")


def transfer_file(file: RemoteFile, target: Path, partial: Path, client: httpx.Client) -> None:
    if target.exists():
        verify_file(target, file)
        return
    if partial.exists():
        metadata = partial.stat()
        if metadata.st_nlink != 1:
            raise ArtifactStoreError(f"hardlinked managed partial is not writable: {partial}")
        offset = metadata.st_size
    else:
        offset = 0
    if offset > file.size_bytes:
        raise ArtifactStoreError(f"oversized partial; remove it before retrying: {partial}")
    if offset == file.size_bytes:
        verify_file(partial, file)
        partial.rename(target)
        return
    headers = {"Accept-Encoding": "identity"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    url = httpx.URL(file.url)
    try:
        for _ in range(6):
            if url.scheme != "https" or url.userinfo:
                raise ArtifactStoreError(
                    "artifact redirects require HTTPS without user credentials"
                )
            with client.stream("GET", url, headers=headers, follow_redirects=False) as response:
                if response.status_code in {301, 302, 303, 307, 308}:
                    location = response.headers.get("location")
                    if not location:
                        raise ArtifactStoreError("artifact redirect has no location")
                    url = response.url.join(location)
                    continue
                if response.status_code not in {200, 206}:
                    raise ArtifactStoreError(
                        f"artifact server returned HTTP {response.status_code}"
                    )
                if response.headers.get("content-encoding", "identity").lower() != "identity":
                    raise ArtifactStoreError("encoded artifact transfers are not accepted")
                if response.status_code == 206:
                    match = re.fullmatch(
                        r"bytes (\d+)-(\d+)/(\d+)", response.headers.get("content-range", "")
                    )
                    if not match:
                        raise ArtifactStoreError("invalid Content-Range")
                    start, end, total = map(int, match.groups())
                    if start != offset or total != file.size_bytes or not start <= end < total:
                        raise ArtifactStoreError(
                            "artifact Content-Range does not match the request"
                        )
                    expected_transfer = end - start + 1
                    mode = "ab"
                else:
                    offset = 0  # A server ignoring Range must replace the partial, never append.
                    expected_transfer = file.size_bytes
                    mode = "wb"
                length = response.headers.get("content-length")
                if length is not None and length != str(expected_transfer):
                    raise ArtifactStoreError("artifact Content-Length mismatch")
                received = 0
                with partial.open(mode) as stream:
                    for chunk in response.iter_bytes():
                        if received + len(chunk) > expected_transfer:
                            raise ArtifactStoreError("artifact response exceeds declared size")
                        stream.write(chunk)
                        received += len(chunk)
                if received != expected_transfer or partial.stat().st_size != file.size_bytes:
                    raise ArtifactStoreError(
                        "incomplete artifact size; partial retained for resume"
                    )
                verify_file(partial, file)
                partial.rename(target)
                return
        raise ArtifactStoreError("too many artifact redirects")
    except httpx.HTTPError as error:
        raise ArtifactStoreError(
            f"transfer interrupted ({type(error).__name__}); partial retained for resume"
        ) from None
