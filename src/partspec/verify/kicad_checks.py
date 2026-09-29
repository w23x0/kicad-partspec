"""Environment-layer check: KiCad itself must be able to load the file."""

from __future__ import annotations

import tempfile
from pathlib import Path

from partspec import config
from partspec.findings import FAIL, WARN, Finding
from partspec.kicad import cli

_TIMEOUT = 120


def check_symbol_loads(library: Path, *, expected_units: int) -> list[Finding]:
    """Export every unit of every symbol to SVG with ``kicad-cli``; success proves KiCad loaded the file."""
    if not _cli_available():
        return [
            Finding(
                "kicad.unavailable",
                WARN,
                "kicad-cli was not found on PATH, so KiCad did not load the file; install KiCad 9 or later to check it.",
            )
        ]
    with tempfile.TemporaryDirectory(prefix="partspec-svg-") as temporary:
        result = cli.run_cli(
            [cli.CLI_COMMAND, "sym", "export", "svg", "-o", temporary, str(library)],
            timeout=config.cli_timeout("PARTSPEC_CLI_TIMEOUT", _TIMEOUT, maximum=3600),
        )
        if result.returncode != 0:
            detail = cli.bounded_output(result.stderr or result.stdout, "output").strip()
            return [
                Finding(
                    "kicad.load_failed",
                    FAIL,
                    f"kicad-cli could not load {library.name} (exit {result.returncode}): {detail or 'no message'}. "
                    "Check pin types and the file format version.",
                    actual=result.returncode,
                )
            ]
        exported = len(list(Path(temporary).glob("*.svg")))
    if exported != expected_units:
        return [
            Finding(
                "kicad.unit_count",
                FAIL,
                f"KiCad exported {exported} unit drawing(s) but the PartSpec needs {expected_units}.",
                expected=expected_units,
                actual=exported,
            )
        ]
    return []


def _cli_available() -> bool:
    try:
        cli.kicad_cli_version()
    except RuntimeError:
        return False
    return True


def check_footprint_loads(library: Path, *, name: str) -> list[Finding]:
    """Export the footprint to SVG with ``kicad-cli``; success proves KiCad loaded the ``.pretty`` folder."""
    if not _cli_available():
        return [
            Finding(
                "kicad.unavailable",
                WARN,
                "kicad-cli was not found on PATH, so KiCad did not load the footprint; install KiCad 9 or later.",
            )
        ]
    with tempfile.TemporaryDirectory(prefix="partspec-svg-") as temporary:
        result = cli.run_cli(
            [cli.CLI_COMMAND, "fp", "export", "svg", "-o", temporary, str(library)],
            timeout=config.cli_timeout("PARTSPEC_CLI_TIMEOUT", _TIMEOUT, maximum=3600),
        )
        if result.returncode != 0:
            detail = cli.bounded_output(result.stderr or result.stdout, "output").strip()
            return [
                Finding(
                    "kicad.load_failed",
                    FAIL,
                    f"kicad-cli could not load {library.name} (exit {result.returncode}): {detail or 'no message'}.",
                    actual=result.returncode,
                )
            ]
        exported = {path.stem for path in Path(temporary).glob("*.svg")}
    if name not in exported:
        return [
            Finding(
                "kicad.footprint_not_found",
                FAIL,
                f"KiCad loaded {library.name} but did not export a footprint named {name!r}.",
                expected=name,
                actual=sorted(exported),
            )
        ]
    return []
