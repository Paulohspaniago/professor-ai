import sqlite3
from pathlib import Path

import pytest

from professor_ai.doctor import inspect_environment
from professor_ai.settings import Settings


def test_missing_optional_model_does_not_block_foundation(tmp_path: Path) -> None:
    data_dir = tmp_path / "future" / "data"

    report = inspect_environment(Settings(data_dir=data_dir))

    assert report.status == "ready"
    assert all(check.status == "ok" for check in report.checks if check.required)
    model = next(check for check in report.checks if check.name == "model")
    assert model.status == "missing"
    assert not model.required
    assert list(tmp_path.iterdir()) == []


def test_missing_fts5_blocks_readiness(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def no_fts5(*args: object, **kwargs: object) -> None:
        raise sqlite3.OperationalError("no such module: fts5")

    monkeypatch.setattr(sqlite3, "connect", no_fts5)

    report = inspect_environment(Settings(data_dir=tmp_path))

    assert report.status == "blocked"
    fts5 = next(check for check in report.checks if check.name == "sqlite_fts5")
    assert fts5.required
    assert fts5.status == "missing"
    assert "FTS5" in fts5.message


def test_unwritable_data_parent_blocks_readiness(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("os.access", lambda path, mode: False)

    report = inspect_environment(Settings(data_dir=tmp_path / "not created"))

    assert report.status == "blocked"
    check = next(check for check in report.checks if check.name == "data_directory")
    assert check.required and check.status == "error"
    assert not (tmp_path / "not created").exists()


def test_data_path_pointing_to_a_file_is_not_writable_storage(tmp_path: Path) -> None:
    data_file = tmp_path / "file.txt"
    data_file.write_text("Existing user content", encoding="utf-8")

    report = inspect_environment(Settings(data_dir=data_file))

    assert report.status == "blocked"
    assert data_file.read_text(encoding="utf-8") == "Existing user content"


def test_diagnostics_preserve_existing_data(tmp_path: Path) -> None:
    document = tmp_path / "study.txt"
    document.write_text("Private learning material", encoding="utf-8")

    report = inspect_environment(Settings(data_dir=tmp_path))

    assert report.status == "ready"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["study.txt"]
    assert document.read_text(encoding="utf-8") == "Private learning material"
