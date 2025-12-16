import pandas as pd
from typing import Dict, Any


def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    missing_data: Dict[str, float] = {}
    for col in df.columns:
        pct = df[col].isnull().mean() * 100
        if pct > 0:
            missing_data[col] = round(float(pct), 2)

    duplicate_rows = int(df.duplicated().sum())

    issues = []
    recommendations = []

    high_missing = [c for c, p in missing_data.items() if p > 50]
    if high_missing:
        issues.append(f"High missing data in columns: {', '.join(high_missing)}")
        recommendations.append(
            "Consider dropping columns with >50% missing data or investigate data collection process"
        )

    if duplicate_rows > 0:
        issues.append(f"{duplicate_rows} duplicate rows found")
        recommendations.append("Remove duplicate rows or investigate if duplicates are intentional")

    object_cols = df.select_dtypes(include=["object"]).columns
    for col in object_cols:
        sample_types = set(type(x).__name__ for x in df[col].dropna().head(100))
        if len(sample_types) > 1:
            issues.append(f"Mixed data types in column '{col}': {sample_types}")
            recommendations.append(f"Standardize data types in column '{col}'")

    score = 100.0
    score -= len(missing_data) * 5
    score -= (duplicate_rows / max(1, len(df))) * 20
    score -= len([col for col, pct in missing_data.items() if pct > 10]) * 10
    score = max(0.0, score)

    if not issues:
        recommendations.append("Data quality looks good! Proceed with analysis.")

    return {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "missing_data": missing_data,
        "duplicate_rows": duplicate_rows,
        "potential_issues": issues,
        "quality_score": round(score, 1),
        "recommendations": recommendations,
    }
