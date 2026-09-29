# kicad-partspec

**Pre-alpha.** Datasheet-derived PartSpec in, verified KiCad symbols and footprints out.

A model reads the datasheet and fills a PartSpec, a JSON file in which every value carries the datasheet page and a
verbatim quote. Deterministic code generates the KiCad files and checks them independently: against the spec, against
the PDF, and by loading them in `kicad-cli`.

The accuracy of model extraction has only been measured on three parts, and the answer key for those was written by
the same author as the skill and has not been reviewed by a human. See
[evals/README.md](https://github.com/w23x0/kicad-partspec/blob/main/evals/README.md) before relying on it.

## Status

| Piece | State |
|---|---|
| PartSpec model, loader, spec-layer checks | done |
| Source check (quotes must appear on the cited datasheet page) | done |
| KiCad symbol generation (multi-unit, alternates, grid-aligned) | done |
| Symbol checks (pins vs spec, grid, overlap, name collisions) | done |
| `kicad-cli` load check | done |
| Footprint generation (dual-row and quad packages, exposed pad) from the datasheet land pattern | done |
| Footprint checks (pads vs datasheet, pads reach leads, silkscreen, courtyard) + `kicad-cli` load | done |
| MCP server (3 tools), skill, plugin manifests | done (plugin install not verified in Claude Code) |
| Extraction evaluation (`evals/score.py`, round 1 in `evals/runs/`) | done, 3 parts only |

## Install

Python 3.10 to 3.13. Not on PyPI yet; from GitHub:

```
pip install "git+https://github.com/w23x0/kicad-partspec"                          # CLI
pip install "kicad-partspec[mcp] @ git+https://github.com/w23x0/kicad-partspec"    # CLI + MCP server
```

Optional tools the checks use when present: KiCad 9 or later (`kicad-cli`, for the load checks; without it you get a
warning instead) and poppler (`pdftotext`, for the datasheet quote check).

The package contains the CLI and the MCP server. The skill that teaches a model how to extract a PartSpec, and the plugin
manifests, live in the repository (`skills/`, `.claude-plugin/`, `.mcp.json`), not in the wheel.

## Use

```
kicad-partspec validate SPEC.json [--datasheet FILE.pdf]
kicad-partspec build SPEC.json --out DIR      # writes <mpn>.kicad_sym and <lib>.pretty/<name>.kicad_mod, verifies both
kicad-partspec verify SPEC.json --symbol FILE --footprint FILE
kicad-partspec-mcp                            # MCP server; PARTSPEC_WORKSPACE limits the paths it may touch
python evals/check_gold.py --datasheets DIR_WITH_PDFS
python evals/score.py --extracted DIR --datasheets DIR_WITH_PDFS   # score model extractions against gold
```

Add `--concise` to print failures in full and warnings only counted by kind.

Gold cases and their conventions are in `evals/README.md`. Generated symbols target the KiCad 9 file format
(version 20241209) and were loaded with KiCad 9.0.9.

Footprints are generated from the datasheet's example land pattern (`land_*` dimensions), not computed from a standard,
so a part whose datasheet has no land pattern gets a symbol and a `footprint.skipped` warning that names the missing
dimensions.

## History

This repository replaces `codex-kicad-mcp`, a read-first MCP server for KiCad projects. Its code is kept in the history
and on the `legacy` branch; the tags `v0.2.0` and `v0.2.1` point at it.

## License

MIT.
