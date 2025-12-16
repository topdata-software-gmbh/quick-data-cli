import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.correlations import find_correlations

console = Console()


def correlations(
    file_path: str,
    threshold: float = typer.Option(0.3, "--threshold"),
    columns: Optional[str] = typer.Option(None, "--columns", help="Comma-separated columns"),
):
    try:
        df = load_data(Path(file_path))
    except Exception as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    cols = [c.strip() for c in columns.split(",")] if columns else None
    result = find_correlations(df, columns=cols, threshold=threshold)
    if "error" in result:
        typer.secho(f"Error: {result['error']}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

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


def register(app: typer.Typer):
    app.command(
        "correlations",
        help="Identify relationships between numerical columns and show strong correlations.",
    )(correlations)
