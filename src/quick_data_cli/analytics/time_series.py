import pandas as pd
import numpy as np
from typing import Dict, Any


def time_series_analysis(
    df: pd.DataFrame,
    date_column: str,
    value_column: str,
    frequency: str = "auto",
) -> Dict[str, Any]:
    if date_column not in df.columns:
        return {"error": f"Date column '{date_column}' not found"}
    if value_column not in df.columns:
        return {"error": f"Value column '{value_column}' not found"}

    df_ts = df.copy()
    df_ts[date_column] = pd.to_datetime(df_ts[date_column])
    df_ts = df_ts.sort_values(date_column)

    date_range = df_ts[date_column].max() - df_ts[date_column].min()

    if frequency == "auto":
        if pd.isna(date_range):
            freq = "D"
        elif getattr(date_range, "days", 0) > 365:
            freq = "M"
        elif getattr(date_range, "days", 0) > 31:
            freq = "W"
        else:
            freq = "D"
    else:
        freq = frequency

    df_ts = df_ts.set_index(date_column)
    ts = df_ts[value_column].resample(freq).mean()

    if len(ts) == 0 or np.all(pd.isna(ts.values)):
        return {"error": "No data points after resampling"}

    x = np.arange(len(ts))
    y = ts.values
    y = np.where(np.isnan(y), np.nanmean(y), y)
    slope, intercept = np.polyfit(x, y, 1)

    result: Dict[str, Any] = {
        "date_column": date_column,
        "value_column": value_column,
        "frequency": freq,
        "date_range": {
            "start": ts.index.min().isoformat(),
            "end": ts.index.max().isoformat(),
            "days": int(getattr(date_range, "days", 0)),
        },
        "trend": {
            "slope": round(float(slope), 4),
            "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
        },
        "statistics": {
            "mean": round(float(np.nanmean(ts.values)), 3),
            "std": round(float(np.nanstd(ts.values)), 3),
            "min": round(float(np.nanmin(ts.values)), 3),
            "max": round(float(np.nanmax(ts.values)), 3),
        },
        "data_points": int(len(ts)),
        "sample_values": {k.isoformat(): (None if pd.isna(v) else float(v)) for k, v in ts.head(10).items()},
    }

    return result
