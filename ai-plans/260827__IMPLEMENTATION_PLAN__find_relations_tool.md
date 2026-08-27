---
filename: "ai-plans/260827__IMPLEMENTATION_PLAN__find_relations_tool.md"
title: "Add a cross-file relationship detection tool to quick-data-cli"
createdAt: 2026-08-27 14:45
updatedAt: 2026-08-27 14:45
status: draft
priority: medium
tags: [mcp, feature, data-profiling, relations]
estimatedComplexity: moderate
documentType: IMPLEMENTATION_PLAN
---

## Problem Overview
The MCP server (`src/quick_data_cli/mcp_server.py`) exposes per-file analytics
(`describe`, `validate_quality`, `correlations`, `segment`, `query`, …) but has
**no first-class way to discover relationships between files in a folder**. The
existing `correlations` tool is *numeric, within-file Pearson r* — a different
concept. Agents currently have to hand-write DuckDB join-coverage queries (e.g.
the manual `alltron-prices` ↔ `lagerbestand` join we ran, which matched
231,477 / 231,525 rows) to find links. We want a dedicated `find_relations` tool
that automatically detects candidate join keys / foreign-key links across the
supplied files and reports overlap coverage. This also feeds the planned global
`analyze-data-files` skill, which will call this tool as its "relationships" step.

## Scope Decision (resolved during brainstorm)
- **Scope A (deliverable):** inter-file link detection only — "file X.col matches
  file Y.col (containment 99.8%, direction 1:N)".
- **Scope B (optional phase 5):** within-file key profiling — flag PK candidates
  (unique high-distinct id) and FK/dimension-key candidates (low-cardinality
  repeating id), and warn when an ID column has no counterpart file in the folder
  (orphan key / possibly a missing lookup). Deferred unless requested.

## Constraints & Assumptions
- Inputs are local file paths (CSV primary; JSON supported by `load_data`). xlsx
  is NOT auto-supported by the loader and is out of scope for v1.
- Files can be large (Alltron feed = 100 MB / 231k rows). Avoid loading every file
  fully into pandas. Use DuckDB `read_csv_auto` and compute intersection counts per
  candidate column pair — same engine the `profile_source` tool already uses.
- The tool is inherently cross-file, so it does NOT use the `_per_file` helper; it
  follows the `query` tool's pattern (accepts the full `file_paths` list).
- Internally manage the `t`/`t0`/`t1` view naming quirk so the agent never sees it.
- Keep result JSON serializable via the existing `_dump`/`_json_default` helpers.

## High-Level Approach
1. Add `analytics/relations.py` with `find_relations(file_paths, **opts)` returning a
   structured report (per file-pair candidate keys ranked by containment %).
2. Register an `@mcp.tool()` `find_relations` in `mcp_server.py` (wire import + JSON dump).
3. Add a Typer CLI command `relations` mirroring the other commands, for human use.
4. Add tests using small fixture CSVs (a parent + child with a shared key).
5. (Optional) Phase 5: within-file key profiling (Scope B).

---

## Phase 1 – Analytics module `analytics/relations.py`
**Objective:** compute candidate cross-file join keys.

- Signature: `find_relations(file_paths, name_similarity=True, min_containment=0.5,
  max_pairs=None) -> Dict[str, Any]`.
- Steps:
  1. For each file, build a lightweight profile via DuckDB: column name, duckdb type,
     distinct count, and a sampled set of distinct values (cap e.g. 5k distinct values
     per column to bound memory; if column has more distinct values than the cap, still
     record distinct *count* and treat as "high cardinality" — only attempt overlap on
     columns whose distinct count <= cap).
  2. Candidate pair generation: for every ordered pair of (file A, column a) × (file B,
     column b) with A != B, consider the pair a candidate if:
     - column names are equal, OR
     - names are similar (token/normalized similarity, e.g. `Artikelnummer 2` vs
       `Nummer 2` share `2` and `nummer` token) when `name_similarity=True`, OR
     - both columns are identifier-like (high distinct, alnum) — low priority.
  3. For each candidate, run a DuckDB query counting `|distinct(a) ∩ distinct(b)|`
     (set intersection) and compute:
     - `containment_a_in_b = overlap / distinct(a)`  (how much of A's key is covered by B)
     - `containment_b_in_a = overlap / distinct(b)`
     - `direction`: `1:1` if both > 0.95, else `1:N` (the side with lower containment is
       the "many" side), else `weak`.
  4. Keep only candidates with `max(containment_a_in_b, containment_b_in_a) >=
     min_containment`. Rank descending by the max containment.
- Return shape:
  ```json
  {
    "file_pairs_checked": N,
    "relations": [
      {
        "file_a": "...", "column_a": "...",
        "file_b": "...", "column_b": "...",
        "distinct_a": 123, "distinct_b": 456,
        "overlap": 120,
        "containment_a_in_b": 0.98,
        "containment_b_in_a": 0.26,
        "direction": "1:N",
        "name_match": true
      }
    ]
  }
  ```
- Reuse `duckdb.from_csv_auto` / `read_csv_auto` (see `profile_source` for the exact
  pattern) rather than pandas, to stay memory-safe on big files.

## Phase 2 – MCP tool registration
**Objective:** expose `find_relations` to agents.

- In `mcp_server.py`: `from .analytics.relations import find_relations`.
- Add:
  ```python
  @mcp.tool()
  def find_relations(
      file_paths: List[str],
      name_similarity: bool = True,
      min_containment: float = 0.5,
  ) -> str:
      """Detect candidate join keys / foreign-key links between files by comparing
      column names and value overlap. Returns ranked relations with containment % and
      direction (1:1 / 1:N). Use when the user asks to 'find relationships between
      these files' or 'detect join keys across this folder'."""
      return _dump(find_relations(file_paths, name_similarity=name_similarity,
                                  min_containment=min_containment))
  ```
- No `_per_file` wrapper; call `find_relations` directly with the full list.

## Phase 3 – CLI command
**Objective:** human-facing `quick-data relations` subcommand (optional but consistent).

- Add `commands/relations_cmd.py` + register in `cli.py` (mirror `query_cmd.py`).
- Positional `file_paths: List[Path]`, options `--name-similarity/--no-name-similarity`
  and `--min-containment`.

## Phase 4 – Tests
**Objective:** prove detection works on a tiny known dataset.

- Fixtures: `parent.csv` (id 1..100, name) and `child.csv` (id 1..100 referencing
  parent, plus 5 orphans). Assert one relation `child.id ↔ parent.id` with
  containment_child_in_parent ≈ 0.95 and direction `1:N` (or `1:1` if no orphans).
- Add a large-file guard test: a column with > cap distinct values is skipped for
  overlap but does not crash.

## Phase 5 – (Optional) within-file key profiling [Scope B]
- Extend `find_relations` (or a sibling `profile_keys`) to flag, per file: PK candidates
  (unique, high-distinct id columns) and FK/dimension candidates (low-cardinality
  repeating id). Warn when an id column has no matching file in the folder.
- Only built if the user confirms Scope B is wanted.

## Validation
- `uv run pytest` passes (new + existing).
- Manual: point the tool at the org-6 `downloaded-files` folder and confirm it
  surfaces `alltron-prices.Artikelnummer 2 ↔ lagerbestand.Nummer 2` (≈99.98%) and
  `privat-produktliste.Warengruppe ↔ warengruppe.Artikelgruppe` if value-overlap holds.
- Confirm a follow-up `analyze-data-files` skill (global skills dir) lists `find_relations`
  as its relationships step.
