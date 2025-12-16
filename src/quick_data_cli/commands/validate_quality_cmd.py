import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.quality import validate_data_quality

console = Console()


def validate_quality(file_path: str):
    try:
        df = load_data(Path(file_path))
    except Exception as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    result = validate_data_quality(df)

    t = Table(title="Data Quality Report")
    t.add_column("Metric")
    t.add_column("Value")
    t.add_row("rows", str(result.get("total_rows")))
    t.add_row("columns", str(result.get("total_columns")))
    t.add_row("quality_score", str(result.get("quality_score")))
    t.add_row("duplicate_rows", str(result.get("duplicate_rows")))
    t.add_row("missing_columns", ", ".join(result.get("missing_data", {}).keys()) or "-")
    console.print(t)

    issues = result.get("potential_issues", [])
    if issues:
        console.rule("Issues")
        for i in issues:
            console.print(f"- {i}")

    recs = result.get("recommendations", [])
    if recs:
        console.rule("Recommendations")
        for r in recs:
            console.print(f"- {r}")


def register(app: typer.Typer):
    app.command(
        "validate-quality",
        help="Run data health checks (missing values, duplicates, mixed types) and return a quality score.",
    )(validate_quality)
