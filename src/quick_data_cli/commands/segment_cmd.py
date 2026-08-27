import typer
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.segment import segment_by_column
from ..utils.file_inputs import prepare_file_inputs

console = Console()


def _run_segment_on_file(file_path: Path, column: str, top_n: int) -> None:
    console.rule(f"[bold cyan]Segment[/bold cyan] :: {file_path}")
    df = load_data(file_path)

    result = segment_by_column(df, column_name=column, top_n=top_n)
    if "error" in result:
        raise RuntimeError(result["error"])

    rows = result["segments"]
    if not rows:
        console.print("No segments.")
        return

    keys = list(rows[0].keys())
    table = Table(title=f"Segments by {result['segmented_by']}", show_header=True, header_style="bold")
    for k in keys:
        table.add_column(str(k))
    for r in rows:
        table.add_row(*[str(r.get(k, "")) for k in keys])

    console.print(table)


def segment(
    file_paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS...",
        help="One or more CSV/JSON files.",
    ),
    column: str = typer.Option(..., "--column"),
    top_n: int = typer.Option(10, "--top-n"),
):
    valid_paths = prepare_file_inputs(file_paths, "segment")
    had_failure = False
    for file_path in valid_paths:
        try:
            _run_segment_on_file(file_path, column, top_n)
        except Exception as e:
            had_failure = True
            typer.secho(
                f"[segment] Failed to process {file_path}: {e}",
                err=True,
                fg=typer.colors.RED,
            )
    if had_failure:
        raise typer.Exit(1)


def register(app: typer.Typer):
    app.command(
        "segment",
        help="Group data by a categorical column and compute aggregate stats for numerical columns.",
    )(segment)
