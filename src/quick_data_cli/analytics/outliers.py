import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any


def detect_outliers(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "iqr",
) -> Dict[str, Any]:
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    existing = [c for c in (columns or []) if c in df.columns]
    if not existing:
        return {"error": "No numerical columns found for outlier detection"}

    outliers_info: Dict[str, Any] = {}
    total = 0

    for col in existing:
        series = df[col].dropna()
        if series.empty:
            outliers_info[col] = {
                "outlier_count": 0,
                "outlier_percentage": 0.0,
                "lower_bound": None,
                "upper_bound": None,
                "outlier_values": [],
                "method": method,
            }
            continue

        if method == "iqr":
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask = (df[col] < lower) | (df[col] > upper)
            outs = df.loc[mask, col]
        elif method == "zscore":
            std = series.std()
            if std == 0 or np.isnan(std):
                outs = series.iloc[0:0]
                lower = float(series.mean())
                upper = float(series.mean())
            else:
                z = np.abs((series - series.mean()) / std)
                outs = series[z > 3]
                lower = float(series.mean() - 3 * std)
                upper = float(series.mean() + 3 * std)
        else:
            return {"error": f"Unsupported method: {method}. Use 'iqr' or 'zscore'"}

        count = int(len(outs))
        total += count
        outliers_info[col] = {
            "outlier_count": count,
            "outlier_percentage": round(count / max(1, len(series)) * 100, 2),
            "lower_bound": None if lower is None else round(float(lower), 3),
            "upper_bound": None if upper is None else round(float(upper), 3),
            "outlier_values": outs.head(10).tolist(),
            "method": method,
        }

    return {
        "method": method,
        "columns_analyzed": existing,
        "total_outliers": total,
        "outliers_by_column": outliers_info,
    }
