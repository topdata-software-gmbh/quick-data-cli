import typer
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.time_series import time_series_analysis
from ..utils.file_inputs import prepare_file_inputs

console = Console()


def _run_time_series_on_file(
    file_path: Path,
    date_column: str,
    value_column: str,
    frequency: str,
) -> None:
    console.rule(f"[bold cyan]Time Series[/bold cyan] :: {file_path}")
    df = load_data(file_path)

    result = time_series_analysis(df, date_column=date_column, value_column=value_column, frequency=frequency)
    if "error" in result:
        raise RuntimeError(result["error"])

    # Summary table
    t = Table(title="Time Series Summary")
    t.add_column("Metric")
    t.add_column("Value")
    t.add_row("frequency", result.get("frequency", ""))
    dr = result.get("date_range", {})
    t.add_row("start", str(dr.get("start")))
    t.add_row("end", str(dr.get("end")))
    t.add_row("days", str(dr.get("days")))
    trend = result.get("trend", {})
    t.add_row("trend_slope", str(trend.get("slope")))
    t.add_row("trend_direction", str(trend.get("direction")))
    stats = result.get("statistics", {})
    for k in ["mean", "std", "min", "max"]:
        t.add_row(k, str(stats.get(k)))
    console.print(t)


def time_series(
    file_paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS...",
        help="One or more CSV/JSON files.",
    ),
    date_column: str = typer.Option(..., "--date-column"),
    value_column: str = typer.Option(..., "--value-column"),
    frequency: str = typer.Option("auto", "--frequency"),
):
    valid_paths = prepare_file_inputs(file_paths, "time-series")
    had_failure = False
    for file_path in valid_paths:
        try:
            _run_time_series_on_file(file_path, date_column, value_column, frequency)
        except Exception as e:
            had_failure = True
            typer.secho(
                f"[time-series] Failed to process {file_path}: {e}",
                err=True,
                fg=typer.colors.RED,
            )
    if had_failure:
        raise typer.Exit(1)


def register(app: typer.Typer):
    app.command(
        "time-series",
        help="Analyze trends over time using a date column and a numerical value column.",
    )(time_series)
