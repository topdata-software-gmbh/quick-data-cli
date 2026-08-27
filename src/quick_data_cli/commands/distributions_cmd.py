import typer
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.distributions import analyze_distributions
from ..utils.file_inputs import prepare_file_inputs

console = Console()


def _run_distributions_on_file(file_path: Path, column: str) -> None:
    console.rule(f"[bold cyan]Distributions[/bold cyan] :: {file_path}")
    df = load_data(file_path)

    result = analyze_distributions(df, column)
    if "error" in result:
        raise RuntimeError(result["error"])

    # Summary table
    summary = Table(title=f"Distribution Summary: {result['column']}")
    summary.add_column("Metric")
    summary.add_column("Value")
    for key in [
        "dtype",
        "total_values",
        "unique_values",
        "null_values",
        "null_percentage",
        "distribution_type",
    ]:
        summary.add_row(key, str(result.get(key)))
    console.print(summary)

    # Detailed
    if result.get("distribution_type") == "numerical":
        t = Table(title="Numerical Stats")
        t.add_column("Metric")
        t.add_column("Value")
        for k in ["mean", "median", "std", "min", "max"]:
            t.add_row(k, str(result.get(k)))
        q = result.get("quartiles", {})
        t.add_row("q25", str(q.get("q25")))
        t.add_row("q50", str(q.get("q50")))
        t.add_row("q75", str(q.get("q75")))
        t.add_row("skewness", str(result.get("skewness")))
        t.add_row("kurtosis", str(result.get("kurtosis")))
        console.print(t)
    else:
        top = result.get("top_10_values", {})
        t = Table(title="Top Values")
        t.add_column("Value")
        t.add_column("Count")
        for k, v in top.items():
            t.add_row(str(k), str(v))
        console.print(t)


def distributions(
    file_paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS...",
        help="One or more CSV/JSON files.",
    ),
    column: str = typer.Argument(..., help="Column to analyze."),
):
    valid_paths = prepare_file_inputs(file_paths, "distributions")
    had_failure = False
    for file_path in valid_paths:
        try:
            _run_distributions_on_file(file_path, column)
        except Exception as e:
            had_failure = True
            typer.secho(
                f"[distributions] Failed to process {file_path}: {e}",
                err=True,
                fg=typer.colors.RED,
            )
    if had_failure:
        raise typer.Exit(1)


def register(app: typer.Typer):
    app.command(
        "distributions",
        help="Analyze a column: show numerical stats or categorical frequency counts.",
    )(distributions)
