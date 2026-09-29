"""The MCP server, exercised over a real stdio connection to a subprocess."""

import asyncio
import json
import os
import shutil
import sys
from pathlib import Path

import pytest

pytest.importorskip("mcp")

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CASES = Path(__file__).resolve().parent.parent / "evals" / "cases"
HAS_KICAD = shutil.which("kicad-cli") is not None


def _run(workspace: Path, calls):
    """Start the server in ``workspace`` and run ``calls(session)``; return its result."""

    async def main():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "kicad_partspec.mcp_server"],
            env={**os.environ, "PARTSPEC_WORKSPACE": str(workspace)},
        )
        async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            return await calls(session)

    return asyncio.run(main())


def _payload(result):
    return result.structured_content if result.structured_content is not None else json.loads(result.content[0].text)


@pytest.fixture
def workspace(tmp_path):
    shutil.copy(CASES / "lm358_soic8" / "spec.gold.json", tmp_path / "lm358.json")
    return tmp_path


def test_three_tools_with_honest_annotations(workspace):
    async def calls(session):
        return (await session.list_tools()).tools

    tools = {tool.name: tool for tool in _run(workspace, calls)}
    assert set(tools) == {"partspec_validate", "partspec_build", "partspec_verify"}
    assert tools["partspec_validate"].annotations.read_only_hint is True
    assert tools["partspec_verify"].annotations.read_only_hint is True
    assert tools["partspec_build"].annotations.read_only_hint is False
    assert tools["partspec_build"].annotations.destructive_hint is False


def test_validate_concise_and_detailed(workspace):
    async def calls(session):
        concise = await session.call_tool("partspec_validate", {"spec_path": "lm358.json"})
        detailed = await session.call_tool(
            "partspec_validate", {"spec_path": "lm358.json", "response_format": "detailed"}
        )
        return _payload(concise), _payload(detailed)

    concise, detailed = _run(workspace, calls)
    assert concise["passed"] is True and concise["failed"] == [] and "findings" not in concise
    assert concise["warning_summary"] == {"status.inferred": 3}
    assert len(detailed["findings"]) == 3 and detailed["findings"][0]["id"] == "status.inferred"


def test_validate_reports_failures_with_a_fix_hint(workspace):
    data = json.loads((workspace / "lm358.json").read_text(encoding="utf-8"))
    data["pins"].pop()

    async def calls(session):
        return _payload(await session.call_tool("partspec_validate", {"spec": data}))

    report = _run(workspace, calls)
    assert report["passed"] is False
    assert (
        report["failed"][0]["id"] == "pins.count_mismatch" and "add the missing pins" in report["failed"][0]["message"]
    )


def test_paths_outside_the_workspace_and_bad_arguments_are_rejected_with_advice(workspace):
    async def calls(session):
        outside = await session.call_tool("partspec_validate", {"spec_path": "/etc/passwd"})
        neither = await session.call_tool("partspec_validate", {})
        missing = await session.call_tool("partspec_validate", {"spec_path": "nope.json"})
        build_out = await session.call_tool("partspec_build", {"spec_path": "lm358.json", "out_dir": "/tmp/elsewhere"})
        return [item.content[0].text for item in (outside, neither, missing, build_out)], [
            item.is_error for item in (outside, neither, missing, build_out)
        ]

    texts, errors = _run(workspace, calls)
    assert all(errors)
    assert "outside the workspace" in texts[0] and "use a path inside it" in texts[0]
    assert "exactly one of spec_path" in texts[1]
    assert "does not exist" in texts[2]
    assert "outside the workspace" in texts[3]
    assert not Path("/tmp/elsewhere").exists()


def test_build_then_verify_round_trip(workspace):
    async def calls(session):
        built = _payload(
            await session.call_tool(
                "partspec_build", {"spec_path": "lm358.json", "out_dir": "out", "check_kicad": HAS_KICAD}
            )
        )
        verified = _payload(
            await session.call_tool(
                "partspec_verify",
                {
                    "spec_path": "lm358.json",
                    "symbol_path": "out/LM358.kicad_sym",
                    "footprint_path": "out/partspec.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod",
                    "check_kicad": HAS_KICAD,
                },
            )
        )
        return built, verified

    built, verified = _run(workspace, calls)
    assert built["passed"] is True
    assert sorted(Path(f).name for f in built["files"]) == ["LM358.kicad_sym", "SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod"]
    assert verified["passed"] is True and verified["failures"] == 0


def test_verify_catches_a_file_that_disagrees_with_the_spec(workspace):
    async def calls(session):
        await session.call_tool("partspec_build", {"spec_path": "lm358.json", "out_dir": "out", "check_kicad": False})
        text = (workspace / "out" / "LM358.kicad_sym").read_text(encoding="utf-8")
        (workspace / "out" / "LM358.kicad_sym").write_text(
            text.replace('(number "3"', '(number "30"'), encoding="utf-8"
        )
        return _payload(
            await session.call_tool(
                "partspec_verify",
                {"spec_path": "lm358.json", "symbol_path": "out/LM358.kicad_sym", "check_kicad": False},
            )
        )

    report = _run(workspace, calls)
    assert report["passed"] is False
    assert {item["id"] for item in report["failed"]} >= {"symbol.pin_missing", "symbol.pin_extra"}


def test_verify_with_no_files_says_what_to_pass(workspace):
    async def calls(session):
        return _payload(await session.call_tool("partspec_verify", {"spec_path": "lm358.json", "check_kicad": False}))

    report = _run(workspace, calls)
    assert report["passed"] is False and "pass a symbol file" in report["failed"][0]["message"]
