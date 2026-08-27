# validate-quality

Run health checks on one or more files: missing values, duplicates, and mixed data types. Each file yields its own report and a quality score (0-100).

Files are processed independently; a failure on one does not stop the others.

```bash
uv run python main.py validate-quality data/employee_survey.csv
uv run python main.py validate-quality data/*.csv
```
