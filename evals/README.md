# Gold cases

Each `cases/<name>/spec.gold.json` is a hand-checked PartSpec for one real part.

| Case | Part | Package | Notes |
|---|---|---|---|
| `lm358_soic8` | TI LM358 | SOIC-8 (D0008A) | dual op-amp, units `A`/`B`/`power` |
| `tps62130_vqfn16` | TI TPS62130 | VQFN-16 (RGT0016C) | exposed pad, several pins per table row |
| `atmega328p_tqfp32` | Microchip ATmega328P | TQFP-32 (drawing MA) | multi-function pins as `alt_names` |

## Status of these cases

They were assembled by Claude from the datasheet text, with the mechanical drawings and pinouts
checked against rendered page images. **They have not been reviewed by a human yet.** Treat them as
a first draft of the answer key until someone has compared them with the datasheets.

## What is checked automatically

- Spec layer (`partspec validate`, and `tests/test_gold.py`): structure, provenance present, pin count,
  unique pin numbers, KiCad pin types, dimension ordering.
- Source layer (`python evals/check_gold.py --datasheets DIR`): every `source.quote` must appear on the
  cited page of the exact PDF (matched by SHA-256). Text comes from `pdftotext -layout`, compared with
  whitespace collapsed.

The quote check proves a quote exists on that page. It does **not** prove that a pin number is bound to
the right name where the datasheet draws them in different places (rotated labels in a pinout figure);
that binding was checked by eye on the rendered page.

The PDFs are not stored here. Download the revision named in each spec (`datasheet.url`, `revision`) and
confirm the SHA-256.

## Conventions

- Dimensions are millimetres. Where the datasheet prints inches with millimetres in brackets, the
  bracketed values are used. A value the datasheet gives only as a range gets `min`/`max`; `TYP` values
  get `nom`.
- Dimension names: `pitch`, `overall_width`, `overall_length`, `body_length`, `body_width`, `body_thickness`,
  `height`, `standoff`, `lead_width`, `lead_length`, `lead_thickness`, `ep_size`.
- `land_*` dimensions come from the datasheet's example land pattern and are reference values, not limits.
- `status`: `extracted` means read directly from the datasheet. `inferred` means the model or the author
  derived it, for example supply and ground pins mapped to KiCad `power_in`, an open-drain output mapped to
  `open_collector`, or the exposed-pad number (the datasheet gives none).
- Parts whose SOIC/TQFP drawing has ambiguous callouts (the SOIC `.004-.010` and `.005-.010` values) leave
  those dimensions out instead of guessing.
