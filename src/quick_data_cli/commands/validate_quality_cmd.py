import typer
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.quality import validate_data_quality
from ..utils.file_inputs import prepare_file_inputs

console = Console()


def _run_validate_quality_on_file(file_path: Path) -> None:
    console.rule(f"[bold cyan]Validate Quality[/bold cyan] :: {file_path}")
    df = load_data(file_path)

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


def validate_quality(
    file_paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS...",
        help="One or more CSV/JSON files.",
    )
):
    valid_paths = prepare_file_inputs(file_paths, "validate-quality")
    had_failure = False
    for file_path in valid_paths:
        try:
            _run_validate_quality_on_file(file_path)
        except Exception as e:
            had_failure = True
            typer.secho(
                f"[validate-quality] Failed to process {file_path}: {e}",
                err=True,
                fg=typer.colors.RED,
            )
    if had_failure:
        raise typer.Exit(1)


def register(app: typer.Typer):
    app.command(
        "validate-quality",
        help="Run data health checks (missing values, duplicates, mixed types) and return a quality score.",
    )(validate_quality)
