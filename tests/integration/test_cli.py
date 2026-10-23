import json
import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from typer.testing import CliRunner

from professor_ai.cli import app

runner = CliRunner()


def test_doctor_json_reports_foundation_ready_without_models(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PROFESSOR_AI_DATA_DIR", str(tmp_path / "untouched"))

    result = runner.invoke(app, ["doctor", "--json"])

    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert set(report) == {"status", "checks"}
    assert report["status"] == "ready"
    for check in report["checks"]:
        assert set(check) == {"name", "required", "status", "message"}
    assert any(
        check["name"] == "model" and check["status"] == "missing" for check in report["checks"]
    )
    assert list(tmp_path.iterdir()) == []


def test_doctor_returns_nonzero_and_valid_json_when_blocked(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def no_sqlite(*args: object, **kwargs: object) -> None:
        raise sqlite3.OperationalError("no such module: fts5")

    monkeypatch.setenv("PROFESSOR_AI_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(sqlite3, "connect", no_sqlite)

    result = runner.invoke(app, ["doctor", "--json"])

    assert result.exit_code == 1
    report = json.loads(result.stdout)
    assert report["status"] == "blocked"
    assert any(
        check["name"] == "sqlite_fts5" and check["status"] == "missing"
        for check in report["checks"]
    )


def test_invalid_doctor_configuration_still_has_machine_readable_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROFESSOR_AI_PORT", "invalid")

    result = runner.invoke(app, ["doctor", "--json"])

    assert result.exit_code == 1
    report = json.loads(result.stdout)
    assert report["status"] == "blocked"
    assert report["checks"][0]["name"] == "configuration"


def test_unresolvable_home_directory_returns_a_json_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROFESSOR_AI_DATA_DIR", "~professor_ai_nonexistent_user/data")

    result = runner.invoke(app, ["doctor", "--json"])

    assert result.exit_code == 1
    report = json.loads(result.stdout)
    assert report["status"] == "blocked"
    check = next(check for check in report["checks"] if check["name"] == "data_directory")
    assert check["status"] == "error"
    assert "PROFESSOR_AI_DATA_DIR" in check["message"]


def test_doctor_has_a_readable_default_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PROFESSOR_AI_DATA_DIR", str(tmp_path))

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "ready" in result.stdout
    assert "model" in result.stdout


def test_serve_uses_validated_loopback_and_port(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    started: list[tuple[str, int, str]] = []

    def run_server(application: FastAPI, *, host: str, port: int) -> None:
        started.append((host, port, application.title))

    monkeypatch.setattr("professor_ai.cli.uvicorn.run", run_server)
    monkeypatch.setenv("PROFESSOR_AI_DATA_DIR", str(tmp_path / "unused"))
    monkeypatch.setenv("PROFESSOR_AI_PORT", "9876")

    result = runner.invoke(app, ["serve"])

    assert result.exit_code == 0, result.output
    assert started == [("127.0.0.1", 9876, "Professor AI")]
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("name", "value"), [("PROFESSOR_AI_HOST", "0.0.0.0"), ("PROFESSOR_AI_PORT", "0")]
)
def test_serve_rejects_invalid_configuration_before_starting(
    name: str, value: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def must_not_start(*args: object, **kwargs: object) -> None:
        pytest.fail("The server must not start with invalid configuration")

    monkeypatch.setattr("professor_ai.cli.uvicorn.run", must_not_start)
    monkeypatch.setenv(name, value)

    result = runner.invoke(app, ["serve"])

    assert result.exit_code == 2
    assert "Invalid configuration" in result.stderr
