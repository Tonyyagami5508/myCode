from __future__ import annotations

import json
from dataclasses import asdict
from typing import Optional

import typer

from .config import load_creds
from .db import list_processes, list_worksteps, query_rows, pick

app = typer.Typer(add_completion=False)


@app.command()
def processes(sn: str = typer.Option(..., "--sn", help="SerialNumber"), format: str = typer.Option("text", "--format", help="text|json")):
    creds = load_creds()
    vals = list_processes(creds, sn)
    if format == "json":
        typer.echo(json.dumps(vals, ensure_ascii=False, indent=2))
    else:
        for v in vals:
            typer.echo(v)


@app.command()
def worksteps(sn: str = typer.Option(..., "--sn"), format: str = typer.Option("text", "--format")):
    creds = load_creds()
    vals = list_worksteps(creds, sn)
    if format == "json":
        typer.echo(json.dumps(vals, ensure_ascii=False, indent=2))
    else:
        for v in vals:
            typer.echo(v)


@app.command(name="query")
def query_cmd(
    sn: str = typer.Option(..., "--sn"),
    process: str = typer.Option("", "--process", help="WorkStepProcessName exact match"),
    process_like: str = typer.Option("", "--process-like", help="SQL LIKE pattern"),
    workstep: str = typer.Option("", "--workstep"),
    select: str = typer.Option("final", "--select", help="final|first|all"),
    limit: int = typer.Option(50, "--limit"),
    format: str = typer.Option("text", "--format", help="text|json"),
):
    creds = load_creds()
    rows = query_rows(creds, sn=sn, process=process, process_like=process_like, workstep=workstep, limit=limit)
    rows = pick(rows, select)

    if format == "json":
        typer.echo(json.dumps([asdict(r) for r in rows], ensure_ascii=False, indent=2))
        raise typer.Exit(0)

    # text
    if not rows:
        typer.echo("(no rows)")
        raise typer.Exit(0)
    for r in rows:
        typer.echo(f"SerialNumber: {r.serial}")
        typer.echo(f"ProductName: {r.product}")
        typer.echo(f"ProcessName: {r.process}")
        typer.echo(f"WorkStep: {r.workstep}")
        typer.echo(f"Result: {r.test_result}  Grade: {r.grade}")
        typer.echo(f"TestEnd: {r.test_end}  UploadDate: {r.upload_date}")
        typer.echo(f"XLSX: {r.result_xlsx}")
        typer.echo(f"JSON: {r.result_json}")
        typer.echo(f"ZIP : {r.result_zip}")
        typer.echo("---")


if __name__ == "__main__":
    app()
