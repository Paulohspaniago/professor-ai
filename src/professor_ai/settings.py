"""Validate local configuration without creating files or loading models."""

from pathlib import Path
from typing import Literal

from platformdirs import user_data_path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROFESSOR_AI_", frozen=True)

    data_dir: Path = Field(default_factory=lambda: user_data_path("ProfessorAI", appauthor=False))
    host: Literal["127.0.0.1"] = "127.0.0.1"
    port: int = Field(default=8765, ge=1, le=65535)


def load_settings() -> Settings:
    return Settings()
