from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Annotated

import boto3
import httpx
import typer

from . import __version__, backup
from .config import load_config
from .health import check_all
from .render import render

app = typer.Typer(no_args_is_help=True, help="Small ops CLI.")


@app.callback()
def main(verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING, format="%(levelname)s %(message)s"
    )


@app.command()
def version() -> None:
    """Print the version."""
    typer.echo(__version__)


@app.command()
def health(
    config: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Check every service in CONFIG. Exit 1 if any is unhealthy."""
    cfg = load_config(config)
    with httpx.Client(follow_redirects=True) as client:
        results = check_all(client, cfg.services)
    if as_json:
        typer.echo(json.dumps([r.__dict__ for r in results], indent=2))
    else:
        for r in results:
            flag = "OK  " if r.ok else "FAIL"
            typer.echo(f"{flag} {r.name:<10} status={r.status} {r.elapsed_ms:.0f}ms {r.detail}")
    raise typer.Exit(code=0 if all(r.ok for r in results) else 1)


@app.command("backup")
def backup_cmd(
    src: Annotated[Path, typer.Argument(exists=True, file_okay=False)],
    bucket: Annotated[str, typer.Option(envvar="SHOP_BUCKET")],
    keep: Annotated[int, typer.Option(min=1)] = 7,
) -> None:
    """Archive SRC and upload it to BUCKET, keeping the newest KEEP archives."""
    key = backup.upload(boto3.client("s3"), bucket, src, keep)
    typer.echo(f"uploaded s3://{bucket}/{key}")


@app.command("render")
def render_cmd(
    template: Annotated[Path, typer.Argument(exists=True)],
    var: Annotated[list[str] | None, typer.Option("--var", help="key=value, repeatable")] = None,
) -> None:
    """Render TEMPLATE with --var key=value pairs."""
    ctx = dict(v.split("=", 1) for v in var or [])
    typer.echo(render(template.read_text(), **ctx), nl=False)
