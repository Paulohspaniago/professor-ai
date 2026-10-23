"""Keep application tests independent of the user's configuration."""

import os

import pytest


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in os.environ:
        if name.startswith("PROFESSOR_AI_"):
            monkeypatch.delenv(name)
