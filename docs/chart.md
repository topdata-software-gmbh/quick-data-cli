# chart

Generate interactive HTML charts (saved to `outputs/charts/`). Supplying multiple files produces a chart per file (output filenames are suffixed with the source file stem when needed).

- `--type` — `bar`, `histogram`, `scatter`, `line`, or `box`.
- `--x` — column for X-axis.
- `--y` — column for Y-axis (optional for histograms/counts).
- `--groupby` — column to color/group data by (optional).
- `--output` — custom output path.

```bash
uv run python main.py chart data/ecommerce_orders.json --type bar --x region --y order_value --groupby product_category
```
