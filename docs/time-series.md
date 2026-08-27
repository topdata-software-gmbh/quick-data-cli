# time-series

Analyze trends over time for each file provided. Requires a date column and a value column.

- `--date-column` — the column containing date/time info.
- `--value-column` — the numerical column to analyze.
- `--frequency` — `D` (daily), `W` (weekly), `M` (monthly), or `auto`.

```bash
uv run python main.py time-series data/ecommerce_orders.json --date-column order_date --value-column order_value
uv run python main.py time-series data/*.csv --date-column date --value-column amount --frequency auto
```
