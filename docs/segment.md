# segment

Group data by a categorical column and calculate aggregate statistics for numerical columns, one file after another.

- `--column` — the categorical column to group by.
- `--top-n` — number of segments to show (default: `10`).

```bash
uv run python main.py segment data/ecommerce_orders.json --column region
```
