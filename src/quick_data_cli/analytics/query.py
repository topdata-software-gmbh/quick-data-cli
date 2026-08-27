"""DuckDB-backed SQL query over one or more data files.

Shared by the ``query`` CLI command and the MCP ``query`` tool so the agent
and the human use the exact same engine. Files are exposed as DuckDB views:
``t`` for a single file, or ``t0``, ``t1``, ... for multiple files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb


def _json_default(obj: Any) -> Any:
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            pass
    if isinstance(obj, (set, frozenset)):
        return list(obj)
    return str(obj)


def _view_sql(file_path: str) -> str:
    """DuckDB read statement appropriate for the file's format, with the path
    inlined (CREATE VIEW cannot take prepared parameters). The path is a
    trusted local file, single quotes are escaped."""
    safe = file_path.replace("'", "''")
    p = Path(file_path)
    suffix = p.suffix.lower()
    if suffix == ".json":
        return f"read_json_auto('{safe}')"
    return f"read_csv_auto('{safe}')"


def query_files(
    file_paths: List[str],
    sql: str,
    max_rows: int = 1000,
) -> Dict[str, Any]:
    """Run ``sql`` against the given files. Returns a JSON-serializable dict
    with ``columns`` and ``rows`` (capped at ``max_rows``)."""
    con = duckdb.connect()
    con.execute("PRAGMA threads=4")

    for i, raw in enumerate(file_paths):
        path = Path(raw)
        if not path.exists() or path.is_dir():
            return {"error": f"file not found: {raw}"}
        name = "t" if len(file_paths) == 1 else f"t{i}"
        read_fn = _view_sql(str(path))
        try:
            con.execute(
                f"CREATE OR REPLACE TEMP VIEW {name} AS SELECT * FROM {read_fn}",
            )
        except Exception as exc:  # noqa: BLE001
            return {"error": f"failed to load {raw}: {type(exc).__name__}: {exc}"}

    try:
        cur = con.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        total = len(rows)
        truncated = total > max_rows
        rows = rows[:max_rows]
        data = [[_json_default(v) for v in row] for row in rows]
        return {
            "columns": cols,
            "row_count": total,
            "returned_rows": len(rows),
            "truncated": truncated,
            "rows": data,
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}", "sql": sql}


def dump_json(payload: Any) -> str:
    return json.dumps(payload, default=_json_default, ensure_ascii=False)
