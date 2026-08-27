# Implementation Plan: MCP Server + DuckDB Hybrid Engine

- **Date:** 2026-08-27
- **Status:** ready
- **ADR:** `_ai/technical_decisions/260827_0933__ADR__mcp-server-and-duckdb-hybrid.md`

## Goal

Expose `quick-data-cli`'s analytics to AI agents as MCP tools (stdio, FastMCP),
add a DuckDB-powered `profile_source` tool for DFG playbook authoring, and update
the documentation. The existing Typer CLI must remain fully functional.

## Design (summary)

- **Transport:** stdio, FastMCP (`mcp` package). `mcp_server.py` + a `quick-data mcp`
  subcommand in `cli.py`.
- **Output:** tools return JSON only. CLI keeps Rich tables.
- **Refactor:** `analytics/*` functions return structured results (dicts); CLI
  commands render them to Rich via a new `presenters/` module.
- **DuckDB:** `profile_source` uses `duckdb.read_csv_auto`.

## Steps

### 1. Dependencies
- Add `mcp>=1.x` and `duckdb>=1.x` to `pyproject.toml`. Run `uv sync`.

### 2. Analytics refactor (return data)
- For each module in `src/quick_data_cli/analytics/` (`describe`, `quality`,
  `correlations`, `segment`, `distributions`, `outliers`, `time_series`, `chart`,
  `execute`): change functions to **return** structured results instead of printing.
- Create `src/quick_data_cli/presenters/` with one Rich-rendering function per
  analytics result, reusing the existing table-building code moved out of the
  commands.
- Update `commands/*_cmd.py` to call analytics → pass result to the matching
  presenter. Verify CLI output is unchanged.

### 3. DuckDB `profile_source`
- New `src/quick_data_cli/analytics/profile_source.py`:
  - `duckdb.read_csv_auto` with sampling for delimiter/encoding/header detection.
  - Per column: inferred type, null %, distinct count, top sample values,
    pattern hints (e.g. looks like SKU/identifier vs free text vs numeric) to aid
    `file_source_url` node authoring (`sku_definition` vs `field_definition`).
  - Returns a structured dict.
- Add a `presenters` entry + a `describe`-style CLI command (`profile`) for manual use.

### 4. MCP server
- New `mcp_server.py` (and `src/quick_data_cli/mcp_server.py` module):
  - FastMCP app, stdio.
  - 10 tools: `describe`, `validate_quality`, `correlations`, `segment`,
    `distributions`, `detect_outliers`, `time_series`, `chart`, `execute`,
    `profile_source`. Each takes `file_paths: list[str]` (+ params) and returns
    `json.dumps(result)`.
  - `chart` returns the output HTML path; `execute` returns captured stdout/result.
- Register a `mcp` subcommand in `cli.py` that launches the server.

### 5. Path handling & safety
- Resolve paths vs CWD. v1 trusts the local filesystem (agent runs locally).
- Optional `base_dir` restriction as a later enhancement (note in docs).

### 6. Documentation
- Update `README.md`: add an "MCP Server" section (what it is, `uv run python
  main.py mcp`, the 10 tools + `profile_source`, JSON output contract, example
  agent usage for authoring DFG playbooks). Keep existing CLI reference intact.
- Add a short `_ai` note only if needed; primary docs are README.

### 7. Tests
- Unit tests: each analytics function returns correct structured results
  (against `data/`).
- MCP smoke test: FastMCP `Client` calling every tool against sample data and
  asserting JSON shape.
- Run `uv run pytest` and `uv run ruff` (if configured) before completion.

## Validation

- `uv run python main.py describe data/*.csv` produces identical Rich output to today.
- `uv run python main.py mcp` starts the server; an MCP client lists 10 tools.
- `profile_source` on a large source CSV (e.g. a 200k-row file) returns schema +
  type/null/pattern profiling quickly without loading all rows into Pandas.
- All tests pass.

## Out of scope (v2)

- HTTP/SSE transport for remote agents.
- `describe`/`validate_quality` moving onto DuckDB (kept on Pandas to limit churn).
- `base_dir` sandboxing.
