from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import plotly.express as px


def create_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_column: str,
    y_column: Optional[str] = None,
    groupby_column: Optional[str] = None,
    title: Optional[str] = None,
    output: Optional[Path] = None,
) -> Dict[str, Any]:
    required = [x_column] + ([y_column] if y_column else []) + ([groupby_column] if groupby_column else [])
    missing = [c for c in required if c and c not in df.columns]
    if missing:
        return {"error": f"Columns not found: {missing}"}

    if title is None:
        title = f"{chart_type.title()} Chart: {x_column}" + (f" vs {y_column}" if y_column else "")
        if groupby_column:
            title += f" (grouped by {groupby_column})"

    fig = None

    if chart_type == "histogram":
        fig = px.histogram(df, x=x_column, color=groupby_column, title=title)
    elif chart_type == "bar":
        if y_column:
            if groupby_column:
                agg_data = df.groupby([x_column, groupby_column])[y_column].mean().reset_index()
                fig = px.bar(agg_data, x=x_column, y=y_column, color=groupby_column, title=title)
            else:
                agg = df.groupby(x_column)[y_column].mean().reset_index()
                fig = px.bar(agg, x=x_column, y=y_column, title=title)
        else:
            if groupby_column:
                counts = df.groupby([x_column, groupby_column]).size().reset_index(name="count")
                fig = px.bar(counts, x=x_column, y="count", color=groupby_column, title=title)
            else:
                counts = df[x_column].value_counts().reset_index()
                counts.columns = [x_column, "count"]
                fig = px.bar(counts, x=x_column, y="count", title=title)
    elif chart_type == "scatter":
        if not y_column:
            return {"error": "Scatter plot requires both x and y"}
        fig = px.scatter(df, x=x_column, y=y_column, color=groupby_column, title=title)
    elif chart_type == "line":
        if not y_column:
            return {"error": "Line plot requires both x and y"}
        df_sorted = df.sort_values(x_column)
        fig = px.line(df_sorted, x=x_column, y=y_column, color=groupby_column, title=title)
    elif chart_type == "box":
        fig = px.box(df, x=x_column, y=y_column, color=groupby_column, title=title)
    else:
        return {"error": "Unsupported chart type: histogram, bar, scatter, line, box"}

    if output is None:
        out_dir = Path("outputs/charts")
        out_dir.mkdir(parents=True, exist_ok=True)
        output = out_dir / f"chart_{chart_type}_{x_column}.html"

    output = Path(output).with_suffix(".html")
    fig.write_html(str(output))

    return {"status": "success", "chart_file": str(output)}
