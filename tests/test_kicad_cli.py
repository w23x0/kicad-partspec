import shutil

import pytest

from partspec import config
from partspec.kicad import cli


def test_missing_cli_raises_runtime_error(monkeypatch):
    monkeypatch.setattr(cli, "CLI_COMMAND", "kicad-cli-definitely-not-installed")
    with pytest.raises(RuntimeError, match="not found"):
        cli.kicad_cli_version()


def test_bounded_output_truncates(monkeypatch):
    monkeypatch.setenv("PARTSPEC_MAX_CLI_OUTPUT_BYTES", "10")
    text = cli.bounded_output("x" * 100, "stdout")
    assert text.startswith("x" * 10)
    assert "[truncated stdout at 10 bytes]" in text


def test_invalid_limit_is_an_error(monkeypatch):
    monkeypatch.setenv("PARTSPEC_MAX_SEXPR_DEPTH", "abc")
    with pytest.raises(ValueError, match="must be an integer"):
        config.max_sexpr_depth()


@pytest.mark.skipif(shutil.which("kicad-cli") is None, reason="kicad-cli not installed")
def test_real_cli_reports_a_version():
    result = cli.kicad_cli_version()
    assert result["exitCode"] == 0
    assert result["version"]
