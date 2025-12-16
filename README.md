# Quick Data CLI

**Quick Data CLI** is a powerful, standalone command-line tool for instant data analysis. It transforms any structured dataset (JSON or CSV) into intelligent insights, visualizations, and quality reports without the need for complex setup or hardcoded schemas.

Built with **Typer**, **Rich**, and **Pandas**, it provides a beautiful, color-coded terminal interface for exploring your data.

## 🚀 Features

*   **Universal Data Support**: Works instantly with any `.csv` or `.json` file.
*   **Zero Configuration**: No schema definitions required; types are inferred automatically.
*   **Rich Terminal Output**: Beautifully formatted tables and logs.
*   **Comprehensive Analytics**:
    *   **Describe**: statistical summaries and data types.
    *   **Correlations**: Heatmap-style correlation discovery.
    *   **Segmentation**: Automatic grouping and aggregation.
    *   **Outliers**: Detection via IQR or Z-Score methods.
    *   **Time Series**: Trend analysis and seasonality detection.
*   **Data Quality**: Automated health checks (missing data, duplicates, mixed types).
*   **Visualization**: Generate interactive Plotly HTML charts.
*   **Custom Scripting**: Execute safe, custom Python logic against your data using the `execute` command.

## 🛠️ Installation & Setup

This project uses `uv` for dependency management.

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd quick-data-cli
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Run the CLI**:
    ```bash
    uv run python main.py --help
    ```

> **Tip:** You can alias this command in your shell for easier access:
> `alias quick-data="uv run python main.py"`

## 📖 Command Reference

### 1. `describe`
Get a high-level overview of your dataset, including shape, column types, missing values, and statistical summaries.

```bash
uv run python main.py describe data/ecommerce_orders.json
```

### 2. `validate-quality`
Run a health check on your data to identify missing values, duplicates, and mixed data types. Returns a quality score (0-100).

```bash
uv run python main.py validate-quality data/employee_survey.csv
```

### 3. `correlations`
Identify relationships between numerical columns.

*   `--threshold`: Minimum correlation strength to display (default: 0.3).
*   `--columns`: Specific columns to analyze (optional).

```bash
uv run python main.py correlations data/product_performance.csv --threshold 0.5
```

### 4. `segment`
Group data by a categorical column and calculate aggregate statistics for numerical columns.

*   `--column`: The categorical column to group by.
*   `--top-n`: Number of segments to show (default: 10).

```bash
uv run python main.py segment data/ecommerce_orders.json --column region
```

### 5. `distributions`
Deep dive into a specific column. Automatically detects if the column is numerical (showing mean, std, quartiles) or categorical (showing frequency counts).

```bash
uv run python main.py distributions data/employee_survey.csv satisfaction_score
```

### 6. `detect-outliers`
Find anomalies in your data.

*   `--method`: Analysis method, either `iqr` (default) or `zscore`.

```bash
uv run python main.py detect-outliers data/product_performance.csv --method zscore
```

### 7. `time-series`
Analyze trends over time. Requires a date column and a value column.

*   `--date-column`: The column containing date/time info.
*   `--value-column`: The numerical column to analyze.
*   `--frequency`: `D` (daily), `W` (weekly), `M` (monthly), or `auto`.

```bash
uv run python main.py time-series data/ecommerce_orders.json --date-column order_date --value-column order_value
```

### 8. `chart`
Generate interactive HTML charts (saved to `outputs/charts/`).

*   `--type`: `bar`, `histogram`, `scatter`, `line`, or `box`.
*   `--x`: Column for X-axis.
*   `--y`: Column for Y-axis (optional for histograms/counts).
*   `--groupby`: Column to color/group data by (optional).
*   `--output`: Custom output path.

```bash
uv run python main.py chart data/ecommerce_orders.json --type bar --x region --y order_value --groupby product_category
```

### 9. `execute`
Run a custom Python script against a loaded dataset. The dataset is injected into your script as a pandas DataFrame named `df`.

**Example Script (`myscript.py`):**
```python
# The CLI injects 'df', 'pd', 'np', and 'plotly' automatically
print("Custom Analysis:")
print(f"Total Revenue: ${df['order_value'].sum():,.2f}")
high_value = df[df['order_value'] > 500]
print(f"High Value Orders: {len(high_value)}")
```

**Run it:**
```bash
uv run python main.py execute data/ecommerce_orders.json myscript.py
```

## 📂 Project Structure

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

## 🧪 Testing

The project includes a comprehensive test suite.

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/quick_data_cli
```

## 📄 License

[MIT](LICENSE)