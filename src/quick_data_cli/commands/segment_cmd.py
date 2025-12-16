import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ..utils.loader import load_data
from ..analytics.segment import segment_by_column

console = Console()


def segment(
    file_path: str,
    column: str = typer.Option(..., "--column"),
    top_n: int = typer.Option(10, "--top-n"),
):
    try:
        df = load_data(Path(file_path))
    except Exception as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    result = segment_by_column(df, column_name=column, top_n=top_n)
    if "error" in result:
        typer.secho(f"Error: {result['error']}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    rows = result["segments"]
    if not rows:
        console.print("No segments.")
        raise typer.Exit(0)

    keys = list(rows[0].keys())
    table = Table(title=f"Segments by {result['segmented_by']}", show_header=True, header_style="bold")
    for k in keys:
        table.add_column(str(k))
    for r in rows:
        table.add_row(*[str(r.get(k, "")) for k in keys])

    console.print(table)


def register(app: typer.Typer):
    app.command(
        "segment",
        help="Group data by a categorical column and compute aggregate stats for numerical columns.",
    )(segment)
