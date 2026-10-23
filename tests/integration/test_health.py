import asyncio
import importlib
from pathlib import Path

import httpx
import pytest

from professor_ai.app import create_app
from professor_ai.settings import Settings


def test_health_works_without_models_or_data_creation(tmp_path: Path) -> None:
    data_dir = tmp_path / "private data"
    app = create_app(Settings(data_dir=data_dir))

    async def request_health() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
        ) as client:
            return await client.get("/health")

    response = asyncio.run(request_health())

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "0.1.0.dev0",
        "model_status": "not_configured",
    }
    assert not data_dir.exists()
    assert list(tmp_path.iterdir()) == []


def test_import_does_not_create_data_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_dir = tmp_path / "unused data"
    monkeypatch.setenv("PROFESSOR_AI_DATA_DIR", str(data_dir))

    importlib.reload(importlib.import_module("professor_ai.app"))

    assert not data_dir.exists()
