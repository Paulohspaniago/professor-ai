"""Commands for diagnosing and serving the local application."""

from typing import Annotated

import typer
import uvicorn
from pydantic import ValidationError

from professor_ai.app import create_app
from professor_ai.doctor import CapabilityCheck, DiagnosticReport, inspect_environment
from professor_ai.evaluation.command import evaluate
from professor_ai.model_artifacts.command import models_app
from professor_ai.settings import load_settings

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Professor AI local foundation.")
app.command()(evaluate)
app.add_typer(models_app, name="models")


def _configuration_error(error: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}"
        for item in error.errors(include_input=False, include_url=False)
    )


@app.command()
def doctor(
    json_output: Annotated[
        bool, typer.Option("--json", help="Print a JSON diagnostic report.")
    ] = False,
) -> None:
    """Check foundation requirements without creating data or downloading models."""
    try:
        report = inspect_environment(load_settings())
    except ValidationError as error:
        report = DiagnosticReport(
            status="blocked",
            checks=[
                CapabilityCheck(
                    name="configuration",
                    required=True,
                    status="error",
                    message=f"Invalid configuration: {_configuration_error(error)}",
                )
            ],
        )

    if json_output:
        typer.echo(report.model_dump_json(indent=2))
    else:
        typer.echo(f"Foundation environment: {report.status}")
        for check in report.checks:
            typer.echo(f"[{check.status}] {check.name}: {check.message}")
    raise typer.Exit(code=1 if report.status == "blocked" else 0)


@app.command()
def serve() -> None:
    """Serve the local health API using validated environment settings."""
    try:
        settings = load_settings()
    except ValidationError as error:
        typer.echo(f"Invalid configuration: {_configuration_error(error)}", err=True)
        raise typer.Exit(code=2) from None
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)
