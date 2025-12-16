import typer
from pathlib import Path
from rich.console import Console
from ..utils.loader import load_data
from ..analytics.chart import create_chart

console = Console()


def chart(
    file_path: str,
    chart_type: str = typer.Option(..., "--type", help="histogram|bar|scatter|line|box"),
    x_column: str = typer.Option(..., "--x"),
    y_column: str = typer.Option(None, "--y"),
    groupby: str = typer.Option(None, "--groupby"),
    output: Path = typer.Option(None, "--output", help="Output HTML path"),
):
    try:
        df = load_data(Path(file_path))
    except Exception as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    result = create_chart(
        df,
        chart_type=chart_type,
        x_column=x_column,
        y_column=y_column,
        groupby_column=groupby,
        output=output,
    )
    if "error" in result:
        typer.secho(f"Error: {result['error']}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    console.print(f"Chart saved to: {result['chart_file']}")


def register(app: typer.Typer):
    app.command("chart")(chart)
