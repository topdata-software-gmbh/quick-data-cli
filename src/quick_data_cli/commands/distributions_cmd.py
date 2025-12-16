import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.distributions import analyze_distributions

console = Console()


def distributions(file_path: str, column: str = typer.Argument(...)):
    try:
        df = load_data(Path(file_path))
    except Exception as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    result = analyze_distributions(df, column)
    if "error" in result:
        typer.secho(f"Error: {result['error']}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

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


def register(app: typer.Typer):
    app.command(
        "distributions",
        help="Analyze a column: show numerical stats or categorical frequency counts.",
    )(distributions)
