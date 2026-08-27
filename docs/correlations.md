# correlations

Identify relationships between numerical columns. Multiple files are analyzed independently with separate tables.

- `--threshold` — minimum correlation strength to display (default: `0.3`).
- `--columns` — specific columns to analyze (optional; defaults to all numeric columns).

Pairs with `|r| > threshold` are reported, labeled `strong` (`|r| > 0.7`) or `moderate`, and tagged `positive` / `negative`.

```bash
uv run python main.py correlations data/product_performance.csv --threshold 0.5
uv run python main.py correlations data/file1.csv data/file2.json --threshold 0.3
```
