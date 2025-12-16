import typer
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data

console = Console()


def describe(file_path: str):
    try:
        df = load_data(Path(file_path))
    except Exception as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    console.print(f"Rows: {df.shape[0]} Columns: {df.shape[1]}")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Column")
    table.add_column("Dtype")
    table.add_column("Non-Null")
    table.add_column("Null %")
    for col in df.columns:
        s = df[col]
        null_pct = s.isna().mean() * 100
        non_null = s.notna().sum()
        table.add_row(str(col), str(s.dtype), str(non_null), f"{null_pct:.2f}")
    console.print(table)

    if not df.select_dtypes(include="number").empty:
        desc = df.describe(include="number")
        t2 = Table(show_header=True, header_style="bold")
        t2.add_column("Metric")
        for c in desc.columns:
            t2.add_column(str(c))
        for idx, row in desc.iterrows():
            t2.add_row(str(idx), *[f"{v:.4g}" if pd.notna(v) else "-" for v in row.values])
        console.print(t2)


def register(app: typer.Typer):
    app.command(
        "describe",
        help="Get an overview of the dataset: shape, column types, missing values, and basic statistics.",
    )(describe)
