---
filename: "ai-plans/251217__IMPLEMENTATION_PLAN__directory_processing_cli.md"
title: "Enable Multi-File Inputs for CLI Commands"
createdAt: 2025-12-17 10:20
updatedAt: 2025-12-17 10:20
status: draft
priority: high
tags: [cli, refactoring, feature]
estimatedComplexity: moderate
documentType: IMPLEMENTATION_PLAN
---

## Problem Overview
Several `quick-data-cli` subcommands (e.g., `describe`, `correlations`, `segment`) currently accept only a single file path. Users need to pass **multiple explicit file paths** (often via shell glob expansion) to run the same command once while processing each file sequentially. The CLI must therefore accept and iterate over multiple positional arguments instead of failing with "unexpected extra arguments." We deliberately **do not** support directory traversal inside the CLI; users must expand directories themselves (e.g., `*_data.csv`).

## Constraints & Assumptions
- Inputs remain limited to CSV/JSON files; commands should validate suffixes just like today.
- Shell globbing will expand wildcards before Typer runs, so commands will receive discrete file paths (no directory recursion logic inside the CLI).
- Commands should fail fast when **all** provided paths are invalid, yet continue processing any remaining files after a per-file error.
- Typer command names, options, and semantics remain backward compatible—only the positional argument changes from single to multi-value.

## High-Level Approach
1. Update Typer command signatures to accept `List[Path]` positional arguments (with `typer.Argument(..., metavar="FILE_PATHS...")`).
2. Refactor each file-based command so that shared per-file logic lives in helpers invoked within a loop over the provided paths.
3. Improve error handling and messaging to call out which file failed while still continuing with the remaining inputs.
4. Update documentation and tests to cover multi-argument usage.
5. Capture work in a follow-up implementation report as required.

---

## Phase 1 – CLI Signature Updates
**Objective:** Allow Typer commands to accept multiple positional file paths.

1. Change each relevant command to receive `file_paths: List[Path] = typer.Argument(..., metavar="FILE_PATHS...")`.
2. Validate that at least one path is supplied; raise `typer.BadParameter` when the list is empty.
3. Perform basic existence checks up front (e.g., `for path in file_paths: ... path.exists()`), surfacing missing files immediately with clear error messages.
4. Preserve existing optional arguments (thresholds, filters, etc.) without changes.

---

## Phase 2 – Per-File Execution Helpers (Describe Example)
**Objective:** Keep the per-file logic isolated while iterating over user-provided paths.

### Steps
1. Extract existing bodies into `_run_<command>_on_file(file_path: Path)` helpers.
2. Iterate over `file_paths`, calling the helper for each.
3. Wrap each helper invocation in `try/except` to log failures (using `typer.secho`) while continuing with the rest.
4. Track whether any invocation failed; exit with non-zero status if so (while still processing all files).

**Sample Refactor** (describe command shown; apply analogous pattern to other commands listed below):

```python
# [MODIFY] src/quick_data_cli/commands/describe_cmd.py
from pathlib import Path
from typing import List


def _describe_file(file_path: Path) -> None:
    console.rule(f"Processing {file_path}")
    df = load_data(file_path)
    ...  # existing describe rendering logic


def describe(file_paths: List[Path]) -> None:
    had_failure = False
    for file_path in file_paths:
        try:
            _describe_file(file_path)
        except Exception as e:
            had_failure = True
            typer.secho(
                f"Failed to describe {file_path}: {e}", fg=typer.colors.RED, err=True
            )
    if had_failure:
        raise typer.Exit(1)
```

### Files to Update
- `src/quick_data_cli/commands/describe_cmd.py`
- `.../correlations_cmd.py`
- `.../segment_cmd.py`
- `.../distributions_cmd.py`
- `.../detect_outliers_cmd.py`
- `.../time_series_cmd.py`
- `.../validate_quality_cmd.py`
- `.../chart_cmd.py`
- `.../execute_cmd.py` (ensure script path handling remains intact; only the data-file argument becomes iterable)

For each file:
1. Introduce helper `_run_<command>_on_file(Path)` encapsulating previous logic.
2. Wrap per-file execution with try/except to keep batch processing resilient.
3. Update docstrings to clarify multi-file support and make console output show which file is being processed.

---

## Phase 3 – Documentation
**Objective:** Communicate new behavior to end users and prevent misuse.

1. Expand the README command sections with explicit multi-file wording (e.g., "Provide one or more CSV/JSON files").
2. Add a "Multiple File Inputs" subsection under general usage with examples using shell globbing (e.g., `uv run python main.py describe data/*.csv`).

```markdown
# [MODIFY] README.md
### Describe
`uv run python main.py describe PATH`

> PATH may point to a single CSV/JSON file or a directory. When a directory is supplied, the command runs sequentially for every file inside (recursively) and prints separators between runs.
```

---

## Phase 4 – Testing & Verification
1. Add command-level tests (or expand existing ones) to verify:
   - Running a command with multiple file paths triggers the helper the same number of times.
   - Errors on one file do not prevent subsequent files from running, yet the exit code is non-zero.
   - Missing files produce readable errors before execution starts.
2. Use `tests/test_custom_analytics_code.py` or new focused tests per command if practical.
3. Manual validation: `uv run python main.py describe data/file1.csv data/file2.csv` and `uv run python main.py describe data/prefix_*`.

---

## Phase 5 – Implementation Report
Upon completion, summarize the work in the mandated report file.

```markdown
# [NEW FILE] ai-plans/251217__IMPLEMENTATION_REPORT__directory_processing_cli.md
- Reference the plan file path in frontmatter (`planFile` field).
- Document files created/modified, testing performed, CLI examples, and doc updates.
```

---

## Documentation & Communication
- README updates covered in Phase 3.
- Implementation report (Phase 5) will capture final outcomes for stakeholders.
- No API/CLI signature changes mean downstream consumers remain unaffected, satisfying the Open/Closed Principle.

## Risk Mitigation
- Incrementally refactor command modules to avoid large diffs.
- Validate directory traversal on a subset of commands before applying the template repo-wide.
- Ensure errors within one file do not halt other files, yet exit code reflects failures (aggregate status or propagate last non-zero).

## Deliverables Summary
1. Updated command modules accepting multi-file positional arguments.
2. Helper abstractions ensuring consistent per-file execution and error handling.
3. README instructions reflecting multiple file inputs + examples.
4. Implementation report documenting outcomes and verification steps.
