"""Read-only capability checks for the application foundation."""

import os
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from professor_ai.settings import Settings


class CapabilityCheck(BaseModel):
    name: str
    required: bool
    status: Literal["ok", "missing", "error"]
    message: str


class DiagnosticReport(BaseModel):
    status: Literal["ready", "blocked"]
    checks: list[CapabilityCheck]


def _check_python() -> CapabilityCheck:
    supported = sys.version_info[:2] == (3, 12)
    return CapabilityCheck(
        name="python",
        required=True,
        status="ok" if supported else "error",
        message=(
            f"Python {sys.version.split()[0]} is supported."
            if supported
            else "Python 3.12 is required. Install it with uv python install 3.12."
        ),
    )


def _check_fts5() -> CapabilityCheck:
    try:
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.execute("CREATE VIRTUAL TABLE capability USING fts5(content)")
            connection.execute("INSERT INTO capability(content) VALUES (?)", ("study",))
            result = connection.execute(
                "SELECT count(*) FROM capability WHERE capability MATCH ?", ("study",)
            ).fetchone()
            if result != (1,):
                raise sqlite3.DatabaseError("FTS5 search did not return its inserted row")
    except sqlite3.Error:
        return CapabilityCheck(
            name="sqlite_fts5",
            required=True,
            status="missing",
            message=(
                "SQLite FTS5 is unavailable. "
                "Use the uv-managed Python 3.12 build in DEVELOPMENT.md."
            ),
        )
    return CapabilityCheck(
        name="sqlite_fts5",
        required=True,
        status="ok",
        message=f"SQLite {sqlite3.sqlite_version} supports FTS5 search.",
    )


def _check_data_directory(path: Path) -> CapabilityCheck:
    try:
        existing = path.expanduser().absolute()
        while not existing.exists() and existing != existing.parent:
            existing = existing.parent
        if not existing.is_dir():
            message = (
                "The data path or its parent is a file. Set PROFESSOR_AI_DATA_DIR to a directory."
            )
        elif not os.access(existing, os.W_OK | os.X_OK):
            message = (
                "The data directory is not writable. Fix permissions or set PROFESSOR_AI_DATA_DIR."
            )
        else:
            return CapabilityCheck(
                name="data_directory",
                required=True,
                status="ok",
                message=(
                    "The data directory or its nearest existing parent is writable; "
                    "no files created."
                ),
            )
    except OSError:
        message = (
            "Cannot inspect the data directory. Check permissions or set PROFESSOR_AI_DATA_DIR."
        )
    return CapabilityCheck(name="data_directory", required=True, status="error", message=message)


def inspect_environment(settings: Settings) -> DiagnosticReport:
    checks = [
        _check_python(),
        _check_fts5(),
        _check_data_directory(settings.data_dir),
        CapabilityCheck(
            name="model",
            required=False,
            status="missing",
            message="No model is configured. The foundation does not require or download a model.",
        ),
    ]
    return DiagnosticReport(
        status="blocked"
        if any(check.required and check.status != "ok" for check in checks)
        else "ready",
        checks=checks,
    )
