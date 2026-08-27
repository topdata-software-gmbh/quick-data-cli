import typer
from pathlib import Path
from typing import List
import subprocess
import shutil
from ..utils.file_inputs import prepare_file_inputs


WRAPPER_CODE = r'''
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


def _run_script_against_file(file_path: Path, script_path: Path) -> int:
    if shutil.which("uv"):
        cmd = ["uv", "run", "python", "-c", WRAPPER_CODE, str(file_path), str(script_path)]
    else:
        cmd = ["python", "-c", WRAPPER_CODE, str(file_path), str(script_path)]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("TIMEOUT: Code execution exceeded 60 seconds") from exc

    if proc.stdout:
        typer.echo(proc.stdout)
    if proc.stderr:
        typer.echo(proc.stderr)

    if proc.returncode != 0:
        raise RuntimeError(f"Script exited with code {proc.returncode}")

    return proc.returncode


def execute(
    paths: List[Path] = typer.Argument(
        ...,
        metavar="FILE_PATHS... SCRIPT_PATH",
        help="One or more CSV/JSON files followed by the Python script to run.",
    ),
):
    if len(paths) < 2:
        raise typer.BadParameter(
            "Provide at least one data file followed by the script path.",
            param_hint="FILE_PATHS... SCRIPT_PATH",
        )

    script_path = paths[-1]
    data_paths = paths[:-1]

    if not script_path.exists() or script_path.is_dir():
        raise typer.BadParameter(
            f"Script file not found or invalid: {script_path}",
            param_hint="SCRIPT_PATH",
        )

    valid_paths = prepare_file_inputs(data_paths, "execute")
    had_failure = False
    for file_path in valid_paths:
        typer.secho(f"[execute] Running {script_path} against {file_path}", fg=typer.colors.CYAN)
        try:
            _run_script_against_file(file_path, script_path)
        except Exception as e:
            had_failure = True
            typer.secho(
                f"[execute] Failed for {file_path}: {e}",
                err=True,
                fg=typer.colors.RED,
            )
    if had_failure:
        raise typer.Exit(1)


def register(app: typer.Typer):
    app.command(
        "execute",
        help="Run a custom Python script against the loaded dataset (available as a pandas DataFrame `df`).",
    )(execute)
