# Quick Data CLI

**Quick Data CLI** is a standalone command-line tool for instant data analysis. It turns any structured dataset (JSON or CSV) into insights, visualizations, and quality reports — no complex setup or hardcoded schemas.

Built with **Typer**, **Rich**, and **Pandas**, it provides a color-coded terminal interface for exploring your data.

## Features

*   **Universal Data Support**: Works instantly with any `.csv` or `.json` file.
*   **Zero Configuration**: No schema definitions; types are inferred automatically.
*   **Rich Terminal Output**: Formatted tables and logs.
*   **Comprehensive Analytics**: describe, correlations, segmentation, outliers, time series, distributions, custom scripting, and SQL.
*   **Data Quality**: Automated health checks (missing data, duplicates, mixed types).
*   **Visualization**: Interactive Plotly HTML charts.
*   **MCP Server**: Expose every command to AI agents.

## Installation & Setup

This project uses `uv` for dependency management.

```bash
git clone <repository-url>
cd quick-data-cli
uv sync
uv run python main.py --help
```

> **Tip:** Alias for easier access: `alias quick-data="uv run python main.py"`

## Analysis Tools

Every analytics command accepts one or more CSV/JSON file paths, processes them sequentially, and reports per-file errors without interrupting the rest.

| Command | Purpose | Docs |
| --- | --- | --- |
| `describe` | Shape, column types, missing values, statistical summaries. | [docs/describe.md](docs/describe.md) |
| `validate-quality` | Health checks (missing, duplicates, mixed types) + quality score. | [docs/validate-quality.md](docs/validate-quality.md) |
| `correlations` | Relationships between numeric columns (threshold-based). | [docs/correlations.md](docs/correlations.md) |
| `segment` | Group by a categorical column, aggregate numeric measures. | [docs/segment.md](docs/segment.md) |
| `distributions` | Distribution of a single column (numeric or categorical). | [docs/distributions.md](docs/distributions.md) |
| `detect-outliers` | Anomaly detection via `iqr` or `zscore`. | [docs/detect-outliers.md](docs/detect-outliers.md) |
| `time-series` | Trend/seasonality analysis over a date × value series. | [docs/time-series.md](docs/time-series.md) |
| `chart` | Interactive Plotly HTML charts. | [docs/chart.md](docs/chart.md) |
| `execute` | Run a custom Python script against each dataset (`df`). | [docs/execute.md](docs/execute.md) |
| `query` | Arbitrary DuckDB SQL against the file(s). | [docs/query.md](docs/query.md) |

Detailed options and examples for each command live in its doc file. A `glob` example that applies to all of them:

```bash
uv run python main.py describe data/*.csv
uv run python main.py correlations data/file1.csv data/file2.json --threshold 0.5
```

## MCP Server

Quick Data CLI can be exposed to AI agents (OpenCode) as an MCP server over stdio. See [docs/mcp-server.md](docs/mcp-server.md) for tools, config, and verification.

```bash
uv run python main.py mcp
```

## Project Structure

```
quick-data-cli/
├── data/                       # Sample datasets
├── outputs/                    # Generated charts and reports
├── src/
│   └── quick_data_cli/
│       ├── analytics/          # Core analysis logic (Pandas/SciPy)
│       ├── commands/           # Typer CLI command definitions
│       ├── core/               # Data models
│       ├── utils/              # File loading utilities
│       ├── cli.py              # Main CLI entry point
│       └── config.py           # Configuration settings
├── tests/                      # Pytest suite
├── main.py                     # Script entry point
└── pyproject.toml              # Dependencies and project config
```

## Testing

```bash
uv run pytest
uv run pytest --cov=src/quick_data_cli
```

## License

[MIT](LICENSE)
