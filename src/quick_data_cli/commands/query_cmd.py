import typer
from pathlib import Path
from typing import List
import json
from rich.console import Console
from rich.table import Table

from ..analytics.query import query_files, dump_json

console = Console()


def query(
    file_paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS...",
        help="One or more CSV/JSON files. Exposed as view 't' (single) or t0, t1, ... (multiple).",
    ),
    sql: str = typer.Option(
        ...,
        "--sql",
        "-s",
        help="DuckDB SQL to run. Reference the data via 't' (single file) or t0, t1, ... (multiple).",
    ),
    output: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: 'table' (default) or 'json'.",
    ),
    max_rows: int = typer.Option(
        1000,
        "--max-rows",
        help="Cap the number of returned rows (json/table).",
    ),
):
    """Run arbitrary DuckDB SQL against the file(s)."""
    paths = [str(p) for p in file_paths]
    result = query_files(paths, sql, max_rows=max_rows)

    if "error" in result:
        typer.secho(result["error"], err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    if output == "json":
        console.print(dump_json(result))
        return

    table = Table(show_header=True, header_style="bold")
    for col in result["columns"]:
        table.add_column(str(col))
    for row in result["rows"]:
        table.add_row(*["" if v is None else str(v) for v in row])
    console.print(table)
    if result["truncated"]:
        skipped = result["row_count"] - result["returned_rows"]
        typer.secho(
            f"... truncated {skipped} of {result['row_count']} rows (use --max-rows)",
            fg=typer.colors.YELLOW,
        )


def register(app: typer.Typer):
    app.command(
        "query",
        help="Run arbitrary DuckDB SQL against one or more CSV/JSON files.",
    )(query)
