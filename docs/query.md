# query

Run arbitrary DuckDB SQL against one or more files. A single file is exposed as view `t`; multiple files as `t0`, `t1`, … Output is a Rich table (default) or JSON (`--output json`). Useful for ad-hoc analysis the built-in commands don't cover.

```bash
# single file -> view 't'
uv run python main.py query data/employee_survey.csv -s "SELECT department, round(avg(satisfaction_score),2) AS avg_sat FROM t GROUP BY department ORDER BY avg_sat DESC"

# multiple files -> t0, t1
uv run python main.py query data/employee_survey.csv data/product_performance.csv -s "SELECT (SELECT count(*) FROM t0) AS survey_rows, (SELECT count(*) FROM t1) AS product_rows"
```
