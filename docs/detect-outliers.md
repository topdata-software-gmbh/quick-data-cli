# detect-outliers

Find anomalies in your data. Errors from one file do not stop the remaining files from being analyzed.

- `--method` — analysis method, either `iqr` (default) or `zscore`.

```bash
uv run python main.py detect-outliers data/product_performance.csv --method zscore
uv run python main.py detect-outliers data/*.csv --method iqr
```
