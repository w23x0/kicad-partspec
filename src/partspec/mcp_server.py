"""MCP server: three tools over ``partspec.api``.

Paths are confined to ``PARTSPEC_WORKSPACE`` (default: the working directory).
A PartSpec can be passed inline or, to save context on large parts, as a file path.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from partspec import api

ResponseFormat = Literal["concise", "detailed"]

mcp = MCPServer(
    "PartSpec",
    instructions=(
        "Turn a datasheet-derived PartSpec into verified KiCad symbols and footprints. "
        "Workflow: fill a PartSpec (see the partspec skill), call partspec_validate with the datasheet PDF until it "
        "passes, then partspec_build. Every value in a PartSpec needs a source page and a verbatim quote. "
        "Paths must be inside PARTSPEC_WORKSPACE."
    ),
)

_READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
_WRITES_FILES = ToolAnnotations(
    read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=False
)


def workspace() -> Path:
    return Path(os.environ.get("PARTSPEC_WORKSPACE") or Path.cwd()).resolve()


def _path(value: str, *, what: str, must_exist: bool = False) -> Path:
    root = workspace()
    candidate = Path(value).expanduser()
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    if not resolved.is_relative_to(root):
        raise ToolError(f"{what} {value!r} is outside the workspace {root}; use a path inside it.")
    if must_exist and not resolved.exists():
        raise ToolError(f"{what} {value!r} does not exist (looked for {resolved}).")
    return resolved


def _spec(spec_path: str | None, spec: dict[str, Any] | None) -> Any:
    if (spec_path is None) == (spec is None):
        raise ToolError("pass exactly one of spec_path (a JSON file) or spec (the PartSpec object).")
    if spec is not None:
        return spec
    assert spec_path is not None
    path = _path(spec_path, what="spec_path", must_exist=True)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise ToolError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ToolError(f"{path} is not valid JSON: {exc}") from exc


@mcp.tool(annotations=_READ_ONLY)
def partspec_validate(
    spec_path: str | None = None,
    spec: dict[str, Any] | None = None,
    datasheet_path: str | None = None,
    response_format: ResponseFormat = "concise",
) -> dict[str, Any]:
    """Check a PartSpec: structure, provenance, pin count, unique pin numbers, KiCad pin types, dimension order.

    With datasheet_path (the PDF) it also confirms the SHA-256 and that every source quote appears on its cited page.
    Fix every entry in "failed" and call again until "passed" is true.
    """
    document = _spec(spec_path, spec)
    datasheet = _path(datasheet_path, what="datasheet_path", must_exist=True) if datasheet_path else None
    return api.summarize(api.validate(document, datasheet), response_format=response_format)


@mcp.tool(annotations=_WRITES_FILES)
def partspec_build(
    out_dir: str,
    spec_path: str | None = None,
    spec: dict[str, Any] | None = None,
    lib_name: str = "partspec",
    check_kicad: bool = True,
    response_format: ResponseFormat = "concise",
) -> dict[str, Any]:
    """Generate a KiCad symbol (and a footprint when the datasheet land pattern is in the spec) and verify them.

    Writes <mpn>.kicad_sym and <lib_name>.pretty/<name>.kicad_mod into out_dir, re-parses them against the spec, and
    loads them with kicad-cli. Nothing is written if the spec itself fails validation.
    """
    document = _spec(spec_path, spec)
    out = _path(out_dir, what="out_dir")
    result = api.build(document, out, lib_name=lib_name, check_kicad=check_kicad)
    return api.summarize(result.findings, result.files, response_format)


@mcp.tool(annotations=_READ_ONLY)
def partspec_verify(
    spec_path: str | None = None,
    spec: dict[str, Any] | None = None,
    symbol_path: str | None = None,
    footprint_path: str | None = None,
    check_kicad: bool = True,
    response_format: ResponseFormat = "concise",
) -> dict[str, Any]:
    """Check existing .kicad_sym and/or .kicad_mod files (from any source) against a PartSpec."""
    document = _spec(spec_path, spec)
    symbol = _path(symbol_path, what="symbol_path", must_exist=True) if symbol_path else None
    footprint = _path(footprint_path, what="footprint_path", must_exist=True) if footprint_path else None
    findings = api.verify_files(document, symbol=symbol, footprint=footprint, check_kicad=check_kicad)
    return api.summarize(findings, response_format=response_format)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
