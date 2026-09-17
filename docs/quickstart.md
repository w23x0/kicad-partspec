# Quick Start

This guide takes a clean machine from the Toolkit catalog to a verified,
read-only KiCad MCP session. The Toolkit itself is metadata and documentation;
the executable server is maintained in the sibling `Codex-KiCad/mcp` checkout or
in the upstream distribution you select.

## Prerequisites

- Codex with MCP support and the `codex` command available on `PATH`.
- Python 3.10 or newer and [`uv`](https://docs.astral.sh/uv/) (recommended).
- KiCad 8 or newer when invoking ERC/DRC; `kicad-cli` must be on `PATH`.
- A disposable or version-controlled directory containing at least one
  `.kicad_pro` project.

Windows 10+, macOS 12+, and Linux are supported; the Linux path below is tested
on Ubuntu/Debian. Confirm the host before changing files:

```bash
codex mcp list
python --version
kicad-cli --version
```

On Ubuntu/Debian install KiCad from the
[KiCad PPA](https://launchpad.net/~kicad/+archive/ubuntu/kicad-10.0) or your
distribution package; `kicad-cli` then lands on `PATH` at `/usr/bin/kicad-cli`.
On Windows PowerShell use `python --version` and `kicad-cli --version` the same
way.

`kicad-cli` is not needed for package installation or read-only parsing, but it
is required for the KiCad version and ERC/DRC tools.

## Install the local KiCad MCP

From the workspace that contains both directories:

```bash
uv run --directory ./Codex-KiCad/mcp pytest -q
uv run --directory ./Codex-KiCad/mcp codex-kicad-mcp
```

The second command stays attached to stdio. Stop it with `Ctrl+C`; Codex normally
owns the process lifecycle. Set the workspace boundary before registering it:

```bash
export KICAD_WORKSPACE="/path/to/eda-workspace"
```

On Windows PowerShell, use `.\Codex-KiCad/mcp`, run `codex-kicad-mcp` directly,
and set the variable with
`$env:KICAD_WORKSPACE = "C:/path/to/eda-workspace"` instead.

## Register with Codex

Copy the KiCad block from [`../catalog/registration.example.toml`](../catalog/registration.example.toml)
into `${CODEX_HOME}/config.toml` (on Linux this is usually
`~/.codex/config.toml`), replacing both paths:

```toml
[mcp_servers.kicad]
command = "uv"
args = ["run", "--directory", "/path/to/Codex-KiCad/mcp", "codex-kicad-mcp"]
env = { KICAD_WORKSPACE = "/path/to/eda-workspace" }
```

On Windows use `C:/path/to/...` paths. Restart Codex and run:

```bash
codex mcp list
```

The server must appear as `kicad` before asking Codex to invoke tools. If it does
not, check the config path, executable path, and inherited environment; do not
label the catalog entry `registered` until the host lists it.

## First safe task

Use a copy of a project and ask Codex to perform this sequence:

1. Discover `.kicad_pro` files below `KICAD_WORKSPACE`.
2. Inspect one project and summarize its schematic, PCB, and metadata files.
3. Run schematic ERC and PCB DRC separately.
4. Report exit codes, issue lines, and any report files created by KiCad.

The current server is read-first. It does not expose routing, library editing,
or arbitrary file writes. KiCad may still create a report during a check, so keep
the first run on a disposable copy and review the diff afterward.

## Record the result

From the Toolkit root, run:

```bash
python scripts/validate_catalog.py
python scripts/check_links.py
```

Update [`../catalog/catalog.json`](../catalog/catalog.json) and [`CONTRIBUTING.md`](../CONTRIBUTING.md) with the date, versions, exact commands, and
observed result. A stale or failed registration is recorded as `needs-review`,
not silently treated as available.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `kicad` is absent from `codex mcp list` | Confirm `${CODEX_HOME}/config.toml` (Linux: `~/.codex/config.toml`), restart Codex, and run the command from a clean shell. |
| No projects are discovered | `KICAD_WORKSPACE` must be an existing directory containing `.kicad_pro`; use paths relative to it. |
| `kicad-cli` cannot be found | Install KiCad and add its CLI directory to `PATH`, then restart Codex. |
| ERC/DRC creates unexpected files | Use a disposable copy, inspect the diff, and document the KiCad version and report path. |
| A command works manually but not in Codex | Compare the environment inherited by Codex with the shell (`PATH`, `KICAD_WORKSPACE`, and `uv` location). |
