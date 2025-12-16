import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.time_series import time_series_analysis

console = Console()


def time_series(
    file_path: str,
    date_column: str = typer.Option(..., "--date-column"),
    value_column: str = typer.Option(..., "--value-column"),
    frequency: str = typer.Option("auto", "--frequency"),
):
    try:
        df = load_data(Path(file_path))
    except Exception as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    result = time_series_analysis(df, date_column=date_column, value_column=value_column, frequency=frequency)
    if "error" in result:
        typer.secho(f"Error: {result['error']}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

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


def register(app: typer.Typer):
    app.command(
        "time-series",
        help="Analyze trends over time using a date column and a numerical value column.",
    )(time_series)
