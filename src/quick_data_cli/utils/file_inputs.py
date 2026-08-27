from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import typer


def prepare_file_inputs(
    file_paths: Iterable[Path],
    command_name: str,
) -> List[Path]:
    """
    Validate CLI file inputs.

    - Ensures at least one argument was supplied.
    - Emits readable errors for any missing paths or directories.
    - Returns only the existing files so commands can keep processing.
    - Raises Typer.BadParameter if all provided paths are invalid.
    """

    collected_paths = [Path(p) for p in file_paths]
    if not collected_paths:
        raise typer.BadParameter(
            "Provide at least one file path.",
            param_hint="FILE_PATHS...",
        )

    valid_paths: List[Path] = []
    invalid_messages: List[str] = []

    for path in collected_paths:
        if not path.exists():
            invalid_messages.append(f"{path} (not found)")
            continue
        if path.is_dir():
            invalid_messages.append(f"{path} (is a directory)")
            continue
        valid_paths.append(path)

    if invalid_messages:
        for message in invalid_messages:
            typer.secho(
                f"[{command_name}] Skipping {message}",
                fg=typer.colors.RED,
                err=True,
            )

    if not valid_paths:
        raise typer.BadParameter(
            f"All provided file paths are invalid for '{command_name}'.",
            param_hint="FILE_PATHS...",
        )

    return valid_paths
