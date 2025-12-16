import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.outliers import detect_outliers

console = Console()


def detect_outliers_cmd(
    file_path: str,
    method: str = typer.Option("iqr", "--method", help="iqr or zscore"),
    columns: Optional[str] = typer.Option(None, "--columns", help="Comma-separated columns"),
):
    try:
        df = load_data(Path(file_path))
    except Exception as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    cols = [c.strip() for c in columns.split(",")] if columns else None
    result = detect_outliers(df, columns=cols, method=method)
    if "error" in result:
        typer.secho(f"Error: {result['error']}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

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


def register(app: typer.Typer):
    app.command(
        "detect-outliers",
        help="Find anomalies in your data using IQR (default) or Z-score.",
    )(detect_outliers_cmd)
