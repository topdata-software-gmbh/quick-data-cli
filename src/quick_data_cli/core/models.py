from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import pandas as pd
import numpy as np


class ColumnInfo(BaseModel):
    name: str
    dtype: str
    unique_values: int
    null_percentage: float
    sample_values: List[Any]
    suggested_role: str

    @classmethod
    def from_series(cls, series: pd.Series, name: str) -> "ColumnInfo":
        if pd.api.types.is_numeric_dtype(series):
            role = "numerical"
        elif pd.api.types.is_datetime64_any_dtype(series):
            role = "temporal"
        elif series.nunique() / len(series) < 0.5:
            role = "categorical"
        elif series.nunique() == len(series):
            role = "identifier"
        else:
            role = "categorical"

        return cls(
            name=name,
            dtype=str(series.dtype),
            unique_values=series.nunique(),
            null_percentage=series.isnull().mean() * 100,
            sample_values=series.dropna().head(3).tolist(),
            suggested_role=role,
        )


class DatasetSchema(BaseModel):
    name: str
    columns: Dict[str, ColumnInfo]
    row_count: int
    suggested_analyses: List[str]

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, name: str) -> "DatasetSchema":
        columns = {}
        for col in df.columns:
            columns[col] = ColumnInfo.from_series(df[col], col)

        suggestions: List[str] = []
        numerical_cols = [col for col, info in columns.items() if info.suggested_role == "numerical"]
        categorical_cols = [col for col, info in columns.items() if info.suggested_role == "categorical"]
        temporal_cols = [col for col, info in columns.items() if info.suggested_role == "temporal"]

        if len(numerical_cols) >= 2:
            suggestions.append("correlation_analysis")
        if categorical_cols:
            suggestions.append("segmentation_analysis")
        if temporal_cols:
            suggestions.append("time_series_analysis")

        return cls(name=name, columns=columns, row_count=len(df), suggested_analyses=suggestions)


loaded_datasets: Dict[str, pd.DataFrame] = {}

dataset_schemas: Dict[str, DatasetSchema] = {}


class DatasetManager:
    @staticmethod
    def load_dataset(file_path: str, dataset_name: str) -> dict:
        if file_path.endswith(".json"):
            df = pd.read_json(file_path)
            file_format = "json"
        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
            file_format = "csv"
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

        loaded_datasets[dataset_name] = df

        schema = DatasetSchema.from_dataframe(df, dataset_name)
        dataset_schemas[dataset_name] = schema

        return {
            "status": "loaded",
            "dataset_name": dataset_name,
            "rows": len(df),
            "columns": list(df.columns),
            "format": file_format,
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB",
        }

    @staticmethod
    def get_dataset(dataset_name: str) -> pd.DataFrame:
        if dataset_name not in loaded_datasets:
            raise ValueError(f"Dataset '{dataset_name}' not loaded. Use load_dataset() first.")
        return loaded_datasets[dataset_name]

    @staticmethod
    def list_datasets() -> List[str]:
        return list(loaded_datasets.keys())

    @staticmethod
    def get_dataset_info(dataset_name: str) -> dict:
        if dataset_name not in loaded_datasets:
            raise ValueError(f"Dataset '{dataset_name}' not loaded")

        df = loaded_datasets[dataset_name]
        schema = dataset_schemas[dataset_name]

        return {
            "name": dataset_name,
            "shape": df.shape,
            "columns": list(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "schema": schema.model_dump(),
        }

    @staticmethod
    def clear_dataset(dataset_name: str) -> dict:
        if dataset_name not in loaded_datasets:
            return {"error": f"Dataset '{dataset_name}' not found"}

        del loaded_datasets[dataset_name]
        del dataset_schemas[dataset_name]

        return {"status": "success", "message": f"Dataset '{dataset_name}' cleared from memory"}

    @staticmethod
    def clear_all_datasets() -> dict:
        count = len(loaded_datasets)
        loaded_datasets.clear()
        dataset_schemas.clear()

        return {"status": "success", "message": f"Cleared {count} datasets from memory"}


class ChartConfig(BaseModel):
    dataset_name: str
    chart_type: str
    x_column: str
    y_column: Optional[str] = None
    groupby_column: Optional[str] = None
    title: Optional[str] = None


class AnalysisResult(BaseModel):
    dataset_name: str
    analysis_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    results: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DataQualityReport(BaseModel):
    dataset_name: str
    total_rows: int
    total_columns: int
    missing_data: Dict[str, float]
    duplicate_rows: int
    potential_issues: List[str]
    quality_score: float
    recommendations: List[str]


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    status: str = "active"
    preferences: Dict[str, Any] = Field(default_factory=dict)
