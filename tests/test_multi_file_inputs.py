import typer
import pytest
from pathlib import Path

from quick_data_cli.commands import describe_cmd, execute_cmd
from quick_data_cli.utils.file_inputs import prepare_file_inputs


def test_prepare_file_inputs_filters_missing(tmp_path, capsys):
    valid_file = tmp_path / "valid.csv"
    valid_file.write_text("a,b\n1,2\n", encoding="utf-8")
    missing_file = tmp_path / "missing.csv"

    result = prepare_file_inputs([valid_file, missing_file], "describe")

    assert result == [valid_file]
    err_output = capsys.readouterr().err
    assert "[describe] Skipping" in err_output
    assert "missing.csv" in err_output


def test_prepare_file_inputs_requires_valid_files(tmp_path):
    missing_file = tmp_path / "missing.csv"
    with pytest.raises(typer.BadParameter):
        prepare_file_inputs([missing_file], "describe")


def test_describe_processes_each_file_and_reports_failures(tmp_path, monkeypatch):
    files = [tmp_path / "first.csv", tmp_path / "second.csv"]
    for f in files:
        f.write_text("a,b\n1,2\n", encoding="utf-8")

    calls: list[Path] = []

    def fake_describe(path: Path) -> None:
        calls.append(path)
        if path.name == "second.csv":
            raise RuntimeError("boom")

    monkeypatch.setattr(describe_cmd, "_describe_file", fake_describe)

    with pytest.raises(typer.Exit) as exc:
        describe_cmd.describe(files)

    assert exc.value.exit_code == 1
    assert calls == files


def test_execute_runs_script_for_each_file(tmp_path, monkeypatch):
    files = [tmp_path / "first.csv", tmp_path / "second.csv"]
    for f in files:
        f.write_text("a,b\n1,2\n", encoding="utf-8")

    script = tmp_path / "script.py"
    script.write_text("print('ok')\n", encoding="utf-8")

    calls: list[Path] = []

    def fake_run(file_path: Path, script_path: Path) -> int:
        calls.append(file_path)
        if file_path.name == "second.csv":
            raise RuntimeError("fail")
        return 0

    monkeypatch.setattr(execute_cmd, "_run_script_against_file", fake_run)

    with pytest.raises(typer.Exit) as exc:
        execute_cmd.execute(files + [script])

    assert exc.value.exit_code == 1
    assert calls == files
