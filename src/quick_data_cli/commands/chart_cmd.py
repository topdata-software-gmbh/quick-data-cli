import typer
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from ..utils.loader import load_data
from ..analytics.chart import create_chart
from ..utils.file_inputs import prepare_file_inputs

console = Console()


def _run_chart_on_file(
    file_path: Path,
    chart_type: str,
    x_column: str,
    y_column: Optional[str],
    groupby: Optional[str],
    output: Optional[Path],
) -> None:
    console.rule(f"[bold cyan]Chart[/bold cyan] :: {file_path}")
    df = load_data(file_path)
    result = create_chart(
        df,
        chart_type=chart_type,
        x_column=x_column,
        y_column=y_column,
        groupby_column=groupby,
        output=output,
    )
    if "error" in result:
        raise RuntimeError(result["error"])

    console.print(f"Chart saved to: {result['chart_file']}")


def _per_file_output(base_output: Optional[Path], file_path: Path, needs_variant: bool) -> Optional[Path]:
    if base_output is None:
        return None
    if not needs_variant:
        return base_output
    suffix = base_output.suffix or ".html"
    name = f"{base_output.stem}_{file_path.stem}{suffix}"
    return base_output.with_name(name)


def chart(
    file_paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS...",
        help="One or more CSV/JSON files.",
    ),
    chart_type: str = typer.Option(..., "--type", help="histogram|bar|scatter|line|box"),
    x_column: str = typer.Option(..., "--x"),
    y_column: Optional[str] = typer.Option(None, "--y"),
    groupby: Optional[str] = typer.Option(None, "--groupby"),
    output: Optional[Path] = typer.Option(None, "--output", help="Output HTML path"),
):
    valid_paths = prepare_file_inputs(file_paths, "chart")
    multiple_files = len(valid_paths) > 1
    had_failure = False
    for file_path in valid_paths:
        derived_output = _per_file_output(output, file_path, multiple_files)
        try:
            _run_chart_on_file(
                file_path,
                chart_type,
                x_column,
                y_column,
                groupby,
                derived_output,
            )
        except Exception as e:
            had_failure = True
            typer.secho(
                f"[chart] Failed to process {file_path}: {e}",
                err=True,
                fg=typer.colors.RED,
            )
    if had_failure:
        raise typer.Exit(1)


def register(app: typer.Typer):
    app.command(
        "chart",
        help="Generate interactive Plotly charts and save them as HTML.",
    )(chart)
