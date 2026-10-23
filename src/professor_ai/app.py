"""Compose the local API without initializing models or storage."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from professor_ai import __version__
from professor_ai.settings import Settings


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = __version__
    model_status: Literal["not_configured"] = "not_configured"


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Professor AI", version=__version__, docs_url=None, redoc_url=None)
    app.state.settings = settings

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    return app
