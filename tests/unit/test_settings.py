from pathlib import Path

import pytest
from pydantic import ValidationError

from professor_ai.settings import Settings, load_settings


def test_defaults_keep_server_local_and_data_outside_checkout() -> None:
    settings = load_settings()

    assert settings.host == "127.0.0.1"
    assert settings.port == 8765
    assert settings.data_dir.is_absolute()
    assert not settings.data_dir.is_relative_to(Path(__file__).resolve().parents[2])


def test_environment_preserves_paths_with_spaces_and_accents(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    location = tmp_path / "Study material" / "Física"
    monkeypatch.setenv("PROFESSOR_AI_DATA_DIR", str(location))
    monkeypatch.setenv("PROFESSOR_AI_PORT", "9876")

    settings = load_settings()

    assert settings.data_dir == location
    assert settings.port == 9876
    assert not location.exists()


@pytest.mark.parametrize("port", [0, -1, 65536])
def test_rejects_invalid_ports(port: int, tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        Settings(data_dir=tmp_path, port=port)


@pytest.mark.parametrize("port", [1, 65535])
def test_accepts_valid_port_boundaries(port: int, tmp_path: Path) -> None:
    assert Settings(data_dir=tmp_path, port=port).port == port


def test_rejects_non_loopback_bind_before_server_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROFESSOR_AI_HOST", "0.0.0.0")

    with pytest.raises(ValidationError):
        load_settings()
