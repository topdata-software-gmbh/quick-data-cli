import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any


def find_correlations(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    threshold: float = 0.3,
) -> Dict[str, Any]:
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    existing_columns = [c for c in columns if c in df.columns]
    if len(existing_columns) < 2:
        return {"error": "Need at least 2 numerical columns for correlation analysis"}

    corr_matrix = df[existing_columns].corr()

    strong_correlations = []
    for i in range(len(existing_columns)):
        for j in range(i + 1, len(existing_columns)):
            v = corr_matrix.iloc[i, j]
            if not pd.isna(v) and abs(v) > threshold:
                strength = "strong" if abs(v) > 0.7 else "moderate"
                direction = "positive" if v > 0 else "negative"
                strong_correlations.append(
                    {
                        "column_1": existing_columns[i],
                        "column_2": existing_columns[j],
                        "correlation": round(float(v), 3),
                        "strength": strength,
                        "direction": direction,
                    }
                )

    strong_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

    return {
        "correlation_matrix": corr_matrix.to_dict(),
        "strong_correlations": strong_correlations,
        "columns_analyzed": existing_columns,
        "threshold": threshold,
    }
