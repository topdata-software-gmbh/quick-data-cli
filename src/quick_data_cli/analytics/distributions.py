import pandas as pd
from typing import Dict, Any

from ..utils.dtypes import display_dtype


def analyze_distributions(df: pd.DataFrame, column_name: str) -> Dict[str, Any]:
    if column_name not in df.columns:
        return {"error": f"Column '{column_name}' not found"}

    s = df[column_name]
    result: Dict[str, Any] = {
        "column": column_name,
        "dtype": display_dtype(s),
        "total_values": int(len(s)),
        "unique_values": int(s.nunique()),
        "null_values": int(s.isnull().sum()),
        "null_percentage": round(float(s.isnull().mean() * 100), 2),
    }

    if pd.api.types.is_numeric_dtype(s):
        result.update(
            {
                "distribution_type": "numerical",
                "mean": round(float(s.mean()), 3) if len(s.dropna()) else 0.0,
                "median": round(float(s.median()), 3) if len(s.dropna()) else 0.0,
                "std": round(float(s.std()), 3) if len(s.dropna()) else 0.0,
                "min": float(s.min()) if len(s.dropna()) else 0.0,
                "max": float(s.max()) if len(s.dropna()) else 0.0,
                "quartiles": {
                    "q25": round(float(s.quantile(0.25)), 3) if len(s.dropna()) else 0.0,
                    "q50": round(float(s.quantile(0.50)), 3) if len(s.dropna()) else 0.0,
                    "q75": round(float(s.quantile(0.75)), 3) if len(s.dropna()) else 0.0,
                },
                "skewness": round(float(s.skew()), 3) if len(s.dropna()) else 0.0,
                "kurtosis": round(float(s.kurtosis()), 3) if len(s.dropna()) else 0.0,
            }
        )
    else:
        value_counts = s.value_counts().head(10)
        result.update(
            {
                "distribution_type": "categorical",
                "most_frequent": value_counts.index[0] if len(value_counts) > 0 else None,
                "frequency_of_most_common": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                "top_10_values": {str(k): int(v) for k, v in value_counts.to_dict().items()},
            }
        )

    return result
