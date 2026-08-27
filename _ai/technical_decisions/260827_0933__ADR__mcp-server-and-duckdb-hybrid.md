# ADR: MCP Server + DuckDB Hybrid Engine for Quick Data CLI

- **Status:** decided
- **Date:** 2026-08-27
- **Project:** quick-data-cli

## Context

`quick-data-cli` is a Typer/Pandas CLI offering 9 analytics commands over CSV/JSON
files. We want AI agents to author **DFG (Data Flow Graph) playbooks** in
`tradeguard-app` by profiling raw source CSVs (delimiter, encoding, column types,
null rates, value patterns) and to QA/analyze DFG outputs and run generic analytics.

Two decisions were brainstormed with the user:

1. **Expose the analytics as an agent-facing MCP tool server** (stdio transport,
   FastMCP), keeping the CLI unchanged.
2. **Adopt DuckDB as a hybrid engine** — DuckDB for load + profiling of large
   source files, Pandas/NumPy/SciPy/Plotly retained for statistical commands.

## Decision

- Add an MCP server (`mcp_server.py`, stdio, FastMCP `mcp` package) exposing one
  tool per existing command **plus a new `profile_source` tool**.
- MCP tools return **JSON only** (no human text summary — the agent consumes
  structured data; manual debugging uses a JSON viewer). The CLI keeps Rich tables.
- Refactor `analytics/*` so each function **returns a structured result**
  (dict/dataclass) instead of printing; CLI commands become thin Rich renderers,
  MCP tools serialize the same result to JSON.
- Use **DuckDB** (`read_csv_auto`) inside `profile_source` for zero-copy profiling
  of 200k+ row files with auto delimiter/encoding/header detection. Other commands
  keep Pandas/NumPy/SciPy/Plotly.

## Consequences

- Positive: agent can author/QA DFG playbooks; large-file profiling is fast and
  memory-safe; single analytics source of truth shared by CLI + MCP.
- Positive: CLI behavior is fully preserved (no regression).
- Negative: refactor touches all 9 analytics modules (mechanical, low risk).
- Negative: adds `mcp` and `duckdb` dependencies.

## Alternatives considered

- *Full DuckDB swap*: rejected — reimplements SciPy stats/correlations/outliers in
  SQL and loses Plotly; high churn for little gain.
- *Single generic `analyze` tool*: rejected — worse tool discovery/descriptions for
  the agent vs one-tool-per-command.
- *Text/markdown-only MCP output*: rejected — agent loses exact numeric precision
  and pays token cost for prose.
- *HTTP/SSE transport*: deferred to v2; stdio is sufficient for local agents.

## Related

- Implementation plan: `_ai/backlog/active/260827_0933__IMPLEMENTATION_PLAN__mcp-server-and-duckdb-hybrid.md`
