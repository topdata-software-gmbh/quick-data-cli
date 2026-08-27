# describe

Get a high-level overview of your dataset: shape, column types, missing values, and statistical summaries.

Provide a single file or multiple files to batch the results. Every file is processed independently and per-file errors are reported without interrupting the rest.

```bash
uv run python main.py describe data/ecommerce_orders.json data/employee_survey.csv
# glob expansion
uv run python main.py describe data/*.csv
```
