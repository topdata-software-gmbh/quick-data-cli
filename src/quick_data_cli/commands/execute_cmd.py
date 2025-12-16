import typer
from pathlib import Path
import subprocess
import shutil


def execute(
    file_path: str = typer.Argument(..., help="Path to CSV or JSON file"),
    script_path: str = typer.Argument(..., help="Path to a Python script to run against the data"),
):
    # Build wrapper code that loads the data and executes the user script with `df` available
    wrapper_code = r'''
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

    cmd = []
    if shutil.which("uv"):
        cmd = ["uv", "run", "python", "-c", wrapper_code, file_path, script_path]
    else:
        cmd = ["python", "-c", wrapper_code, file_path, script_path]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        typer.secho("TIMEOUT: Code execution exceeded 60 seconds", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    if proc.stdout:
        typer.echo(proc.stdout)
    if proc.stderr:
        typer.echo(proc.stderr)

    raise typer.Exit(proc.returncode)


def register(app: typer.Typer):
    app.command("execute")(execute)
