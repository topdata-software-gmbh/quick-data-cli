# MCP Server

Quick Data CLI can be exposed to AI agents (such as OpenCode) as an MCP server over stdio transport. Launch it directly with:

```bash
uv run python main.py mcp
```

This starts a stdio MCP server that exposes the analytics commands as agent-facing tools.

## Tools

The server exposes one tool per analytics command, plus a DuckDB-powered profiler:

| Tool | Purpose |
| --- | --- |
| `describe` | Shape, column types, missing values, numeric stats. |
| `validate_quality` | Missing data, duplicates, mixed-type checks, quality score. |
| `correlations` | Strong correlations (|r| ≥ threshold) between numeric columns. |
| `segment` | Group by a categorical column and aggregate numeric measures. |
| `distributions` | Distribution of a single column (numeric stats or category counts). |
| `detect_outliers` | Outlier counts via `iqr` or `zscore`. |
| `time_series` | Resample/summarize a date × value series. |
| `chart` | Render a Plotly HTML chart; returns the output file path. |
| `execute` | Run a custom Python script against each dataset (`df`). |
| `query` | Run arbitrary DuckDB SQL against the file(s) (`t` / `t0`,`t1`, ...). |
| `profile_source` | DuckDB profiling of a raw source CSV (types, null %, distinct counts, pattern hints) for DFG playbook authoring. |

**Output contract:** every tool takes `file_paths: list[str]` (plus optional parameters) and returns a JSON string — a list of per-file results. No human text is emitted, so the agent receives exact, token-efficient structured data. Errors are returned as structured `{"error": "..."}` entries rather than crashing the server.

**Example agent usage:** profile a raw source CSV to decide `sku_definition` vs `field_definition` nodes, then QA a DFG output with `validate_quality` / `correlations`.

## Add to local (project) config

Create or edit `opencode.json` in your project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "quick-data": {
      "type": "local",
      "command": ["uv", "--directory", "/topdata/quick-data-cli", "run", "python", "main.py", "mcp"],
      "enabled": true
    }
  }
}
```

The `--directory` flag points `uv` at the project so the server works regardless of the agent's current working directory.

## Add to global config

To make the server available in every project, add the same `mcp` block to your global OpenCode config at `~/.config/opencode/opencode.json`.

## Verify

After editing, confirm the server is detected and connected:

```bash
opencode mcp list
```
