# distributions

Deep dive into a single column across one or more datasets. Automatically detects whether the column is numerical (showing mean, std, quartiles) or categorical (showing frequency counts).

```bash
uv run python main.py distributions data/employee_survey.csv satisfaction_score
uv run python main.py distributions data/*.csv some_column
```
