"""Explicit model catalog, acquisition and integrity commands."""

import json
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from pydantic import BaseModel

from professor_ai.model_artifacts.catalog import (
    Artifact,
    Catalog,
    artifact_fingerprint,
    find_artifact,
    load_catalog,
)
from professor_ai.model_artifacts.store import ArtifactStoreError, fetch_artifact, verify_artifact
from professor_ai.settings import load_settings

models_app = typer.Typer(
    no_args_is_help=True, help="Inspect, acquire and verify pinned local models."
)
CatalogOption = Annotated[
    Path | None, typer.Option("--catalog", help="Override the packaged catalog.")
]
DirectoryOption = Annotated[Path | None, typer.Option("--directory", help="Model store directory.")]
JsonOption = Annotated[bool, typer.Option("--json", help="Print a machine-readable JSON result.")]


def _emit(value: BaseModel | dict[str, object], as_json: bool) -> None:
    data = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    typer.echo(json.dumps(data, ensure_ascii=False, indent=None if as_json else 2))


def _error(error: Exception, as_json: bool, code: int) -> NoReturn:
    if as_json:
        _emit({"status": "invalid" if code == 2 else "failed", "error": str(error)[:2000]}, True)
    else:
        typer.echo(f"Model operation failed: {error}", err=True)
    raise typer.Exit(code=code) from None


def _catalog(path: Path | None, as_json: bool) -> Catalog:
    try:
        return load_catalog(path)
    except (OSError, ValueError, RuntimeError) as error:
        _error(error, as_json, 2)


def _entry(artifact_id: str, path: Path | None, as_json: bool) -> Artifact:
    try:
        return find_artifact(_catalog(path, as_json), artifact_id)
    except ValueError as error:
        _error(error, as_json, 2)


def _root(directory: Path | None, as_json: bool) -> Path:
    try:
        return (
            directory if directory is not None else load_settings().data_dir / "models"
        ).expanduser()
    except (OSError, ValueError, RuntimeError) as error:
        _error(error, as_json, 2)


@models_app.command("list")
def list_models(catalog: CatalogOption = None, json_output: JsonOption = False) -> None:
    """List pinned candidates offline; this does not inspect or create a model store."""
    loaded = _catalog(catalog, json_output)
    _emit(
        {
            "status": "catalog",
            "checked_on": loaded.checked_on.isoformat(),
            "runtime_qualified": False,
            "artifacts": [
                {
                    "id": a.id,
                    "role": a.role,
                    "license": a.license,
                    "size_bytes": sum(f.size_bytes for f in a.files),
                    "verification": a.verification,
                }
                for a in loaded.artifacts
            ],
        },
        json_output,
    )


@models_app.command("inspect")
def inspect_model(
    artifact_id: str, catalog: CatalogOption = None, json_output: JsonOption = False
) -> None:
    """Show immutable sources, hashes and proposed settings without network access."""
    artifact = _entry(artifact_id, catalog, json_output)
    _emit(
        {
            "status": "catalog",
            "fingerprint": artifact_fingerprint(artifact),
            "runtime_qualified": False,
            "size_bytes": sum(f.size_bytes for f in artifact.files),
            "artifact": artifact.model_dump(mode="json"),
        },
        json_output,
    )


@models_app.command("verify")
def verify_model(
    artifact_id: str,
    catalog: CatalogOption = None,
    directory: DirectoryOption = None,
    json_output: JsonOption = False,
) -> None:
    """Read and hash local files; no download or inference is performed."""
    artifact = _entry(artifact_id, catalog, json_output)
    report = verify_artifact(artifact, _root(directory, json_output))
    _emit(report, json_output)
    raise typer.Exit(code=0 if report.status == "verified" else 1)


@models_app.command("fetch")
def fetch_model(
    artifact_id: str,
    catalog: CatalogOption = None,
    directory: DirectoryOption = None,
    json_output: JsonOption = False,
) -> None:
    """Explicitly download/resume one candidate and verify its complete local snapshot."""
    artifact = _entry(artifact_id, catalog, json_output)
    root = _root(directory, json_output)
    typer.echo(
        f"Acquiring {artifact.id}: {sum(f.size_bytes for f in artifact.files)} bytes; "
        "this verifies files, not inference readiness.",
        err=True,
    )
    try:
        report = fetch_artifact(artifact, root)
    except (OSError, ArtifactStoreError) as error:
        _error(error, json_output, 1)
    _emit(report, json_output)
    raise typer.Exit(code=0 if report.status == "verified" else 1)
