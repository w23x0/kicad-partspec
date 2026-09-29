# partspec

Work in progress. Datasheet-derived PartSpec in, verified KiCad symbols and footprints out.

The model extracts a PartSpec with a source for every value; deterministic code generates and verifies the KiCad files.

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
| MCP server and skill | not started |

## Use

```
partspec validate SPEC.json
partspec build SPEC.json --out DIR      # writes <mpn>.kicad_sym and <lib>.pretty/<name>.kicad_mod, verifies both
python evals/check_gold.py --datasheets DIR_WITH_PDFS
```

Gold cases and their conventions are in `evals/README.md`. Generated symbols target the KiCad 9 file
format (version 20241209) and were loaded with KiCad 9.0.9.

Footprints are generated from the datasheet's example land pattern (`land_*` dimensions), not computed
from a standard, so a part whose datasheet has no land pattern gets a symbol and a `footprint.skipped`
warning that names the missing dimensions.
