import pandas as pd
import numpy as np
from typing import Dict, Any, List


def segment_by_column(
    df: pd.DataFrame,
    column_name: str,
    method: str = "auto",
    top_n: int = 10,
) -> Dict[str, Any]:
    if column_name not in df.columns:
        return {"error": f"Column '{column_name}' not found"}

    numerical_cols: List[str] = df.select_dtypes(include=[np.number]).columns.tolist()
    if column_name in numerical_cols:
        numerical_cols.remove(column_name)

    if not numerical_cols:
        segments = df.groupby(column_name).size().to_frame("count")
        segments = segments.sort_values("count", ascending=False).head(top_n)
    else:
        agg_dict = {col: ["count", "mean", "sum", "std"] for col in numerical_cols}
        segments = df.groupby(column_name).agg(agg_dict)
        segments.columns = ["_".join(col).strip() for col in segments.columns]
        if len(segments.columns) > 0:
            segments = segments.sort_values(by=segments.columns[0], ascending=False)
        segments = segments.head(top_n)

    total_rows = len(df)
    if "count" in segments.columns:
        segments["percentage"] = (segments["count"] / total_rows * 100).round(2)
    else:
        counts = df.groupby(column_name).size()
        segments["count"] = counts
        segments["percentage"] = (counts / total_rows * 100).round(2)

    return {
        "segmented_by": column_name,
        "segment_count": int(len(segments)),
        "segments": segments.reset_index().to_dict(orient="records"),
        "total_rows": int(total_rows),
        "numerical_columns_analyzed": numerical_cols,
    }
