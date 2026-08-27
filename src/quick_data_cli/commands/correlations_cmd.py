import typer
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.correlations import find_correlations
from ..utils.file_inputs import prepare_file_inputs

console = Console()


def _run_correlations_on_file(
    file_path: Path,
    threshold: float,
    columns: Optional[str],
) -> None:
    console.rule(f"[bold cyan]Correlations[/bold cyan] :: {file_path}")
    df = load_data(file_path)
    cols = [c.strip() for c in columns.split(",")] if columns else None
    result = find_correlations(df, columns=cols, threshold=threshold)
    if "error" in result:
        raise RuntimeError(result["error"])

    table = Table(title="Strong Correlations", show_header=True, header_style="bold")
    table.add_column("Column 1")
    table.add_column("Column 2")
    table.add_column("Correlation")
    table.add_column("Strength")
    table.add_column("Direction")

    for row in result["strong_correlations"]:
        table.add_row(
            row["column_1"],
            row["column_2"],
            f"{row['correlation']:.3f}",
            row["strength"],
            row["direction"],
        )

    console.print(table)


def correlations(
    file_paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS...",
        help="One or more CSV/JSON files.",
    ),
    threshold: float = typer.Option(0.3, "--threshold"),
    columns: Optional[str] = typer.Option(None, "--columns", help="Comma-separated columns"),
):
    valid_paths = prepare_file_inputs(file_paths, "correlations")
    had_failure = False
    for file_path in valid_paths:
        try:
            _run_correlations_on_file(file_path, threshold, columns)
        except Exception as e:
            had_failure = True
            typer.secho(
                f"[correlations] Failed to process {file_path}: {e}",
                err=True,
                fg=typer.colors.RED,
            )
    if had_failure:
        raise typer.Exit(1)


def register(app: typer.Typer):
    app.command(
        "correlations",
        help="Identify relationships between numerical columns and show strong correlations.",
    )(correlations)
