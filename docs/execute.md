# execute

Run a custom Python script against one or more datasets. The dataset is injected into your script as a pandas DataFrame named `df`, and the script runs sequentially for each provided file.

The CLI also injects `pd`, `np`, and `plotly` automatically.

**Example script (`myscript.py`):**

```python
# The CLI injects 'df', 'pd', 'np', and 'plotly' automatically
print("Custom Analysis:")
print(f"Total Revenue: ${df['order_value'].sum():,.2f}")
high_value = df[df['order_value'] > 500]
print(f"High Value Orders: {len(high_value)}")
```

**Run it:**

```bash
uv run python main.py execute data/ecommerce_orders.json data/employee_survey.csv myscript.py
```
