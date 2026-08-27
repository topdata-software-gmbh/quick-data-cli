import typer
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.outliers import detect_outliers
from ..utils.file_inputs import prepare_file_inputs

console = Console()


def _run_detect_outliers_on_file(
    file_path: Path,
    method: str,
    columns: Optional[str],
) -> None:
    console.rule(f"[bold cyan]Detect Outliers[/bold cyan] :: {file_path}")
    df = load_data(file_path)

    cols = [c.strip() for c in columns.split(",")] if columns else None
    result = detect_outliers(df, columns=cols, method=method)
    if "error" in result:
        raise RuntimeError(result["error"])

    table = Table(title=f"Outliers ({method})", show_header=True, header_style="bold")
    table.add_column("Column")
    table.add_column("Count")
    table.add_column("%")
    table.add_column("Lower")
    table.add_column("Upper")

    for col, info in result["outliers_by_column"].items():
        table.add_row(
            col,
            str(info.get("outlier_count")),
            str(info.get("outlier_percentage")),
            str(info.get("lower_bound")),
            str(info.get("upper_bound")),
        )

    console.print(table)


def detect_outliers_cmd(
    file_paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS...",
        help="One or more CSV/JSON files.",
    ),
    method: str = typer.Option("iqr", "--method", help="iqr or zscore"),
    columns: Optional[str] = typer.Option(None, "--columns", help="Comma-separated columns"),
):
    valid_paths = prepare_file_inputs(file_paths, "detect-outliers")
    had_failure = False
    for file_path in valid_paths:
        try:
            _run_detect_outliers_on_file(file_path, method, columns)
        except Exception as e:
            had_failure = True
            typer.secho(
                f"[detect-outliers] Failed to process {file_path}: {e}",
                err=True,
                fg=typer.colors.RED,
            )
    if had_failure:
        raise typer.Exit(1)


def register(app: typer.Typer):
    app.command(
        "detect-outliers",
        help="Find anomalies in your data using IQR (default) or Z-score.",
    )(detect_outliers_cmd)
