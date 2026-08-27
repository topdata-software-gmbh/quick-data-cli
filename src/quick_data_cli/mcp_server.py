"""MCP server exposing quick-data-cli analytics to AI agents (stdio, FastMCP).

Each tool accepts ``file_paths`` (list of local file paths) plus optional
parameters and returns a JSON string of the structured analytics result.
The existing Typer CLI remains the human-facing interface; this server is
the machine-facing interface sharing the same analytics source of truth.
"""

from __future__ import annotations

import json
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from mcp.server.fastmcp import FastMCP

from .utils.loader import load_data
from .utils.dtypes import display_dtype
from .analytics.correlations import find_correlations
from .analytics.quality import validate_data_quality
from .analytics.segment import segment_by_column
from .analytics.distributions import analyze_distributions
from .analytics.outliers import detect_outliers
from .analytics.time_series import time_series_analysis
from .analytics.chart import create_chart


mcp = FastMCP("quick-data")


# --------------------------------------------------------------------------- #
# JSON helpers
# --------------------------------------------------------------------------- #
def _json_default(obj: Any) -> Any:
    if isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()
    if isinstance(obj, (pd.Timedelta,)):
        return str(obj)
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            pass
    if isinstance(obj, (set, frozenset)):
        return list(obj)
    return str(obj)


def _dump(payload: Any) -> str:
    return json.dumps(payload, default=_json_default, ensure_ascii=False)


def _per_file(file_paths: List[str], fn) -> List[Dict[str, Any]]:
    """Run ``fn(df, path)`` for each existing file; collect per-file results."""
    results: List[Dict[str, Any]] = []
    for raw in file_paths:
        path = Path(raw)
        if not path.exists() or path.is_dir():
            results.append({"file": str(path), "error": f"not found: {path}"})
            continue
        try:
            df = load_data(path)
            results.append(fn(df, path))
        except Exception as exc:  # noqa: BLE001 - report to agent, do not crash server
            results.append({"file": str(path), "error": f"{type(exc).__name__}: {exc}"})
    return results


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #
@mcp.tool()
def describe(file_paths: List[str]) -> str:
    """Overview of one or more datasets: shape, column types, missing values,
    and basic numeric statistics. Returns a JSON list of per-file summaries."""

    def _one(df: pd.DataFrame, path: Path) -> Dict[str, Any]:
        numeric = df.select_dtypes(include="number")
        column_stats = []
        for col in df.columns:
            s = df[col]
            null_pct = float(s.isna().mean() * 100)
            column_stats.append(
                {
                    "column": str(col),
                    "dtype": display_dtype(s),
                    "non_null": int(s.notna().sum()),
                    "null_pct": round(null_pct, 2),
                }
            )
        out: Dict[str, Any] = {
            "file": str(path),
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_stats": column_stats,
        }
        if not numeric.empty:
            desc = numeric.describe()
            out["numeric_describe"] = {
                str(idx): {
                    str(c): (None if pd.isna(v) else float(v))
                    for c, v in row.items()
                }
                for idx, row in desc.iterrows()
            }
        return out

    return _dump(_per_file(file_paths, _one))


@mcp.tool()
def validate_quality(file_paths: List[str]) -> str:
    """Validate data quality (missing data, duplicates, type issues) for each
    file. Returns a JSON list of per-file quality reports."""

    return _dump(_per_file(file_paths, lambda df, p: {
        "file": str(p), **validate_data_quality(df)
    }))


@mcp.tool()
def correlations(
    file_paths: List[str],
    columns: Optional[List[str]] = None,
    threshold: float = 0.3,
) -> str:
    """Find strong correlations (|r| >= threshold) between numeric columns.
    Returns a JSON list of per-file correlation results."""

    return _dump(_per_file(file_paths, lambda df, p: {
        "file": str(p), **find_correlations(df, columns=columns, threshold=threshold)
    }))


@mcp.tool()
def segment(
    file_paths: List[str],
    column: str,
    method: str = "auto",
    top_n: int = 10,
) -> str:
    """Segment the dataset by a categorical column and aggregate numeric
    measures. Returns a JSON list of per-file segmentations."""

    return _dump(_per_file(file_paths, lambda df, p: {
        "file": str(p), **segment_by_column(df, column, method=method, top_n=top_n)
    }))


@mcp.tool()
def distributions(file_paths: List[str], column: str) -> str:
    """Analyze the distribution of a single column (value counts / numeric
    histogram stats). Returns a JSON list of per-file analyses."""

    return _dump(_per_file(file_paths, lambda df, p: {
        "file": str(p), **analyze_distributions(df, column)
    }))


@mcp.tool()
def detect_outliers(
    file_paths: List[str],
    columns: Optional[List[str]] = None,
    method: str = "iqr",
) -> str:
    """Detect outliers in numeric columns using 'iqr' or 'zscore'.
    Returns a JSON list of per-file outlier reports."""

    return _dump(_per_file(file_paths, lambda df, p: {
        "file": str(p), **detect_outliers(df, columns=columns, method=method)
    }))


@mcp.tool()
def time_series(
    file_paths: List[str],
    date_column: str,
    value_column: str,
    frequency: str = "auto",
) -> str:
    """Resample and summarize a time series. Returns a JSON list of per-file
    time-series analyses."""

    return _dump(_per_file(file_paths, lambda df, p: {
        "file": str(p),
        **time_series_analysis(df, date_column, value_column, frequency=frequency),
    }))


@mcp.tool()
def chart(
    file_paths: List[str],
    chart_type: str,
    x_column: str,
    y_column: Optional[str] = None,
    groupby_column: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """Render a Plotly chart (histogram/bar/scatter/line/box) to an HTML file
    and return its path. Returns a JSON list of per-file results."""

    def _one(df: pd.DataFrame, path: Path) -> Dict[str, Any]:
        out_dir = Path(output_dir) if output_dir else (path.parent / "outputs" / "charts")
        out_dir.mkdir(parents=True, exist_ok=True)
        output = out_dir / f"chart_{chart_type}_{x_column}.html"
        return create_chart(
            df,
            chart_type=chart_type,
            x_column=x_column,
            y_column=y_column,
            groupby_column=groupby_column,
            output=output,
        )

    return _dump(_per_file(file_paths, _one))


@mcp.tool()
def execute(file_paths: List[str], script_path: str) -> str:
    """Run a custom Python script against each dataset (the DataFrame is
    available as ``df``). Returns captured stdout/stderr per file as JSON."""

    script = Path(script_path)
    if not script.exists() or script.is_dir():
        return _dump({"error": f"script not found: {script_path}"})

    results: List[Dict[str, Any]] = []
    for raw in file_paths:
        path = Path(raw)
        if not path.exists() or path.is_dir():
            results.append({"file": str(path), "error": f"not found: {path}"})
            continue
        try:
            cmd = ["uv", "run", "python", "-c", _WRAPPER, str(path), str(script)] \
                if shutil.which("uv") else \
                ["python", "-c", _WRAPPER, str(path), str(script)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            results.append({
                "file": str(path),
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            })
        except subprocess.TimeoutExpired:
            results.append({"file": str(path), "error": "TIMEOUT: exceeded 60 seconds"})
        except Exception as exc:  # noqa: BLE001
            results.append({"file": str(path), "error": f"{type(exc).__name__}: {exc}"})

    return _dump(results)


@mcp.tool()
def profile_source(file_paths: List[str]) -> str:
    """Profile raw source CSVs with DuckDB (auto delimiter/encoding/header
    detection) without loading all rows into Pandas. For each file returns
    inferred column types, null %, distinct counts, top sample values and
    pattern hints (SKU/identifier vs free text vs numeric) to aid DFG
    playbook authoring. Returns a JSON list of per-file profiles."""

    import duckdb

    def _pattern_hint(series_sample: List[Any]) -> str:
        vals = [str(v) for v in series_sample if v is not None]
        if not vals:
            return "empty"
    non_empty = [v for v in vals if v != ""]
    if not non_empty:
        return "empty"
    # numeric?
    numeric = sum(1 for v in non_empty if v.lstrip("-").replace(".", "", 1).isdigit())
    if numeric >= 0.9 * len(non_empty):
        return "numeric"
    # identifier-like: high cardinality, short tokens, alnum (allow _ - .)
    distinct = len(set(non_empty))
    avg_len = sum(len(v) for v in non_empty) / len(non_empty)
    alnum = sum(1 for v in non_empty if v.replace("_", "").replace("-", "").replace(".", "").isalnum())
    if distinct >= 0.8 * len(non_empty) and alnum >= 0.8 * len(non_empty) and avg_len < 40:
        return "identifier_or_sku"
    if distinct >= 0.8 * len(non_empty):
        return "high_cardinality_text"
    return "categorical_or_text"

    results: List[Dict[str, Any]] = []
    for raw in file_paths:
        path = Path(raw)
        if not path.exists() or path.is_dir():
            results.append({"file": str(path), "error": f"not found: {path}"})
            continue
        try:
            # Relation API gives columns/types without loading all rows.
            rel = duckdb.from_csv_auto(str(path), sample_size=-1)
            cols = list(rel.columns)
            col_types = list(rel.dtypes)
            safe_path = str(path).replace("'", "''")
            con = duckdb.connect()
            con.execute("PRAGMA threads=4")
            con.execute(f"CREATE TEMP VIEW src AS SELECT * FROM read_csv_auto('{safe_path}')")
            total = con.execute("SELECT count(*) FROM src").fetchone()[0]
            profile: Dict[str, Any] = {
                "file": str(path),
                "rows": int(total),
                "columns": len(cols),
                "column_profiles": [],
            }
            for col, dtype in zip(cols, col_types):
                null_q = f'SELECT count(*) FROM src WHERE "{col}" IS NULL'
                distinct_q = f'SELECT count(DISTINCT "{col}") FROM src'
                sample_q = f'SELECT "{col}" FROM src WHERE "{col}" IS NOT NULL LIMIT 5'
                try:
                    nulls = int(con.execute(null_q).fetchone()[0])
                    distinct = int(con.execute(distinct_q).fetchone()[0])
                    sample = [r[0] for r in con.execute(sample_q).fetchall()]
                except Exception:
                    nulls = None
                    distinct = None
                    sample = []
                null_pct = round(nulls / total * 100, 2) if (nulls is not None and total) else None
                profile["column_profiles"].append({
                    "column": col,
                    "duckdb_type": str(dtype),
                    "null_count": nulls,
                    "null_pct": null_pct,
                    "distinct_count": distinct,
                    "top_samples": [str(s) for s in sample],
                    "pattern_hint": _pattern_hint(sample),
                })
            con.close()
            results.append(profile)
        except Exception as exc:  # noqa: BLE001
            results.append({"file": str(path), "error": f"{type(exc).__name__}: {exc}"})

    return _dump(results)


_WRAPPER = r'''
import sys
import pandas as pd
import numpy as np
from pathlib import Path

file_path = Path(sys.argv[1])
script_path = Path(sys.argv[2])

if not file_path.exists():
    print(f"ERROR: Data file not found: {file_path}")
    raise SystemExit(2)
if not script_path.exists():
    print(f"ERROR: Script file not found: {script_path}")
    raise SystemExit(2)

suffix = file_path.suffix.lower()
if suffix == '.csv':
    df = pd.read_csv(file_path)
elif suffix == '.json':
    df = pd.read_json(file_path)
else:
    print(f"ERROR: Unsupported file format: {suffix}")
    raise SystemExit(2)

ns = {"df": df, "pd": pd, "np": np}
code = script_path.read_text(encoding='utf-8')
try:
    exec(compile(code, str(script_path), 'exec'), ns, ns)
except Exception as e:
    import traceback
    print(f"ERROR: {type(e).__name__}: {e}")
    print("Traceback:")
    print(traceback.format_exc())
    raise SystemExit(1)
'''


def run() -> None:
    """Entry point for the ``quick-data mcp`` subcommand."""
    mcp.run()


if __name__ == "__main__":
    run()
