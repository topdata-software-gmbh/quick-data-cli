import pandas as pd
from pandas.api.types import (
    infer_dtype,
    is_bool_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_object_dtype,
    is_string_dtype,
)


def display_dtype(series: pd.Series) -> str:
    if is_string_dtype(series.dtype):
        return "string"
    if is_object_dtype(series.dtype):
        non_null = series.dropna()
        if not non_null.empty:
            inferred = infer_dtype(non_null, skipna=True)
            if inferred in {"string", "unicode", "bytes"}:
                return "string"

    if is_bool_dtype(series.dtype):
        return "bool"
    if is_integer_dtype(series.dtype):
        return "int"
    if is_float_dtype(series.dtype):
        return "float"
    return str(series.dtype)
