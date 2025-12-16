import typer
from .cli_config import CLI_CONTEXT_SETTINGS

app = typer.Typer(
    context_settings=CLI_CONTEXT_SETTINGS,
    name="quick-data",
    help="A CLI for quick, intelligent data analysis on any CSV or JSON file."
)

from .commands import (
    describe_cmd,
    correlations_cmd,
    segment_cmd,
    distributions_cmd,
    detect_outliers_cmd,
    time_series_cmd,
    validate_quality_cmd,
    chart_cmd,
    execute_cmd,
)

describe_cmd.register(app)
correlations_cmd.register(app)
segment_cmd.register(app)
distributions_cmd.register(app)
detect_outliers_cmd.register(app)
time_series_cmd.register(app)
validate_quality_cmd.register(app)
chart_cmd.register(app)
execute_cmd.register(app)

def main():
    app()
