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

- Spec layer (`kicad-partspec validate`, and `tests/test_gold.py`): structure, provenance present, pin count,
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

## Extraction round 1

Six independent model runs (each gold case twice) extracted a PartSpec from the datasheet PDF with the skill in
`skills/partspec/`, using the CLI validator with the PDF in the loop. Outputs are in `runs/round1/`, scores in
`runs/round1_scores_*.json`; reproduce with `python evals/score.py --extracted evals/runs/round1 --datasheets DIR`.

| Score | Original gold | Corrected gold |
|---|---|---|
| Usable without edit (symbol and footprint identical to gold, every quote on its page) | **2/6** | **4/6** |
| Pin numbers found | 100% | 100% |
| Pin names right | 100% | 100% |

| Run | types right | dims right | quotes not on page | usable (original / corrected) |
|---|---|---|---|---|
| lm358 run1 / run2 | 8/8, 8/8 | 10/10, 10/10 | 0/19, 0/20 | yes/yes, yes/yes |
| tps62130 run1 | 17/17 | 11/12 | 0/29 | no/yes |
| tps62130 run2 | 14/17 | 9/12 | 0/29 | no/no |
| atmega328p run1 | 32/32 | 11/11 | 0/43 | no/yes |
| atmega328p run2 | 30/32 | 11/11 | 0/43 | no/no |

Types are scored against the corrected gold.

### What the disagreements were

- Two were gold mistakes, found after seeing the results: ATmega328P `PC6` (gold said `input`; KiCad's official symbol and both
  runs say `bidirectional`) and an `alt_names` entry on the exposed pad that the skill's own definition of `alt_names` excludes.
- Four were skill gaps, fixed afterwards: supply pins whose I/O column says `I` (`power_in` was not stressed), ADC channels
  read as `passive`, `X ± t` dimensions, and stacked max/min pairs. Both TPS62130 runs also dropped the `±` tolerance of the
  exposed pad; that dimension does not affect the generated files.
- No run invented a pin, a pin number or a name. Every failure was a pin type or the min/max of a dimension.

### Read these numbers with care

- Three parts, two runs each. This shows where extraction breaks, not a reliable accuracy rate.
- The gold was written by the same author as the skill, and two gold entries were corrected after the results were seen, so
  the corrected column is not independent. The skill was then edited to close the gaps the runs exposed; the next honest test
  needs datasheets that were not used to write either.
- "Quotes not on page" is measured with the validator in the loop: runs saw failures and fixed them (one run failed once
  before passing). It is not a first-attempt rate.
- The runs used the default subagent model of the session. Isolation from the gold files was by instruction only, not enforced.
- Status labels: both ATmega runs over-marked `inferred` (15 and 22 pins beyond gold) and never under-marked; the only
  under-marked pins were the three TPS62130 supply pins that run 2 got wrong. Over-marking is the safe direction.
