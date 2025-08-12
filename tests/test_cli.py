from __future__ import annotations

from typer.testing import CliRunner

from kforge.cli import app


def test_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ls" in result.stdout
    assert "run" in result.stdout
    assert "stop" in result.stdout
