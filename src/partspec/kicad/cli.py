"""kicad-cli subprocess adapter.

All external KiCad invocations go through ``run_cli`` with fixed safe process
defaults and bounded output.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from partspec import config

CLI_COMMAND = "kicad-cli"
DEFAULT_VERSION_TIMEOUT = 15


def bounded_output(value: Any, label: str) -> str:
    """Convert subprocess output to bounded UTF-8 text."""
    if value is None:
        text = ""
    elif isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace")
    else:
        text = str(value)
    limit = config.max_cli_output_bytes()
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= limit:
        return text
    clipped = encoded[:limit].decode("utf-8", errors="replace")
    return clipped + f"\n[truncated {label} at {limit} bytes]"


def run_cli(command: list[str], *, timeout: int, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run a KiCad CLI command with safe process defaults."""
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("kicad-cli was not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"kicad-cli timed out after {timeout} seconds") from exc
    except PermissionError as exc:
        raise RuntimeError("kicad-cli could not be executed (permission denied)") from exc
    except OSError as exc:
        raise RuntimeError(f"kicad-cli could not be executed: {exc.strerror or exc.__class__.__name__}") from exc


def kicad_cli_version() -> dict[str, object]:
    result = run_cli(
        [CLI_COMMAND, "--version"],
        timeout=config.cli_timeout("PARTSPEC_CLI_VERSION_TIMEOUT", DEFAULT_VERSION_TIMEOUT, maximum=300),
    )
    stdout = bounded_output(result.stdout, "stdout")
    stderr = bounded_output(result.stderr, "stderr")
    # Some KiCad builds print the version on stderr.
    version = stdout.strip() or stderr.strip()
    return {"exitCode": result.returncode, "version": version, "stderr": stderr}
