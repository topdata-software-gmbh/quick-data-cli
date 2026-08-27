import typer
from pathlib import Path
from typing import List
import pandas as pd
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..utils.dtypes import display_dtype
from ..utils.file_inputs import prepare_file_inputs

console = Console()


def _format_number(v) -> str:
    if pd.isna(v):
        return "-"
    try:
        fv = float(v)
    except Exception:
        return str(v)

    if fv.is_integer():
        return str(int(fv))

    s = f"{fv:.6f}"
    return s.rstrip("0").rstrip(".")


def _describe_file(file_path: Path) -> None:
    console.rule(f"[bold cyan]Describe[/bold cyan] :: {file_path}")
    df = load_data(file_path)

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
        table.add_row(str(col), display_dtype(s), str(non_null), f"{null_pct:.2f}")
    console.print(table)

    if not df.select_dtypes(include="number").empty:
        desc = df.describe(include="number")
        t2 = Table(show_header=True, header_style="bold")
        t2.add_column("Metric")
        for c in desc.columns:
            t2.add_column(str(c))
        for idx, row in desc.iterrows():
            t2.add_row(str(idx), *[_format_number(v) for v in row.values])
        console.print(t2)


def describe(
    file_paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS...",
        help="One or more CSV/JSON files.",
    )
):
    valid_paths = prepare_file_inputs(file_paths, "describe")
    had_failure = False
    for file_path in valid_paths:
        try:
            _describe_file(file_path)
        except Exception as e:
            had_failure = True
            typer.secho(
                f"[describe] Failed to process {file_path}: {e}",
                err=True,
                fg=typer.colors.RED,
            )
    if had_failure:
        raise typer.Exit(1)


def register(app: typer.Typer):
    app.command(
        "describe",
        help="Get an overview of the dataset: shape, column types, missing values, and basic statistics.",
    )(describe)
