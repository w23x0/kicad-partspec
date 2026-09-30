# Gold cases

Each `cases/<name>/spec.gold.json` is a hand-checked PartSpec for one real part.

| Case | Part | Package | Notes |
|---|---|---|---|
| `lm358_soic8` | TI LM358 | SOIC-8 (D0008A) | dual op-amp, units `A`/`B`/`power` |
| `tps62130_vqfn16` | TI TPS62130 | VQFN-16 (RGT0016C) | exposed pad, several pins per table row |
| `atmega328p_tqfp32` | Microchip ATmega328P | TQFP-32 (drawing MA) | multi-function pins as `alt_names` |
| `ina219_soic8` | TI INA219 | SOIC-8 (D0008A) | round 2 |
| `txs0108e_tssop20` | TI TXS0108E | TSSOP-20 (PW0020A) | round 2; one part with two ports, no units |
| `ads1115_vssop10` | TI ADS1115 | VSSOP-10 (DGS0010A) | round 2; open-drain output |
| `tps54202_sot23` | TI TPS54202 | SOT-23-6 (DDC0006A) | round 2 |
| `rp2040_qfn56` | Raspberry Pi RP2040 | QFN-56, exposed pad | round 2; 642-page datasheet, pin names disagree between figure and tables |
| `74hc595_so16` | Nexperia 74HC595 | SO16 (SOT109-1) | round 2; no land pattern in the datasheet, so no footprint; 3-state outputs |
| `stm32g030_tssop20` | ST STM32G030F6 | TSSOP-20 | round 2; letter-coded outline table |
| `cp2102n_qfn24` | Silicon Labs CP2102N | QFN-24, exposed pad | round 2; one datasheet for three packages |

## Status of these cases

They were assembled by Claude from the datasheet text, with the mechanical drawings and pinouts
checked against rendered page images. **They have not been reviewed by a human yet.** Treat them as
a first draft of the answer key until someone has compared them with the datasheets.

The round-2 cases were also cross-checked against the official KiCad library symbol and footprint; each case's
`review.md` lists every disagreement with KiCad and how it was decided. Reading the disagreements with the extraction
runs afterwards still found two gold errors (see round 2), which is why a human review is still needed.

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

## Extraction round 2

Eight parts that were used to write neither the skill nor the round-1 gold, from five vendors, two runs each. Outputs are
in `runs/round2/`, scores in `runs/round2_scores.json`; reproduce with
`python evals/score.py --extracted evals/runs/round2 --datasheets DIR`.

How it was run:

- Each run started in an empty directory holding only the datasheet PDF, with the plugin loaded from this repository
  (`claude --plugin-dir`, so the skill and the MCP server as a user gets them), headless, told to finish without asking.
- Model: `space-bunny-free` through OpenCode Go for every run and every gold author. Not a Claude model, and not the
  model of round 1, so the two rounds are not comparable.
- Isolation by ordering, not by instruction: a case's gold was written only after both of its runs had finished.
- Gold: written by a separate run with every pin and dimension checked on a rendered page, then cross-checked against the
  official KiCad symbol and footprint (`cases/<case>/review.md`). Every disagreement between a run and the gold was then
  decided on the rendered page by the orchestrating session (Claude Opus). That found two gold errors, both corrected:
  74HC595 `lead_length` mixed `L` and `Lp`, and TPS54202 `standoff` was the lead thickness. Neither affects the
  generated files.
- The ST and Silicon Labs PDFs were fetched from Wayback Machine snapshots of the vendor URLs, because both vendor sites
  refused scripted downloads. The SHA-256 in each gold file is of the PDF actually used.
- Scored with the code of this commit (after the pitch-check fix and SOT-23 support below).

| Run | types | dims | quotes not on page | usable as scored | usable after adjudication |
|---|---|---|---|---|---|
| ina219 run1 / run2 | 8/8, 8/8 | 10/10, 10/10 | 0/20, 0/20 | yes, yes | yes, yes |
| ads1115 run1 / run2 | 10/10, 10/10 | 12/12, 12/12 | 0/22, 0/22 | yes, yes | yes, yes |
| tps54202 run1 / run2 | 5/6, 6/6 | 12/12, 10/12 | 0/18, 0/17 | no, yes | no, yes |
| txs0108e run1 / run2 | 20/20, 20/20 | 12/12, 11/12 | 0/32, 0/33 | no, no | no, no |
| 74hc595 run1 / run2 | 15/16, 8/16 | 8/10, 9/10 | 0/25, 0/26 | no, no | no, no |
| rp2040 run1 / run2 | 57/57, 57/57 | 7/7, 7/7 | 0/64, 0/64 | no, no | yes, yes |
| stm32g030 run1 / run2 | 19/20, 19/20 | 13/13, 11/13 | 0/33, 0/33 | no, no | no, no |
| cp2102n run1 / run2 | 22/25, 21/25 | 8/12, 12/12 | 0/37, 0/37 | no, no | no, no |
| **total** | | | | **5/16** | **7/16** |

Adjudication accepted two kinds of disagreement: the RP2040 datasheet names pins 25 and 56 differently in its pinout
figure (`SWDIO`, `QSPI_SS_N`) and its pin tables (`SWD`, `QSPI_CSn`), and the runs took the table names; and for CP2102N
pins with no printed direction (`D+`, `D-`, `RSTb`) the runs followed the skill's `passive` rule where the gold followed
KiCad. Either answer counts. The CP2102N land table prints one value across its Min/Max columns, recorded as `nom` by the
gold and `max` by one run; the footprint is the same, so it is not counted against the run.

### What went wrong

- No run invented a pin, a pin number or a name, and every run found every pin.
- Units: both TXS0108E runs split one level translator into units `A`, `B` and `power` by its two ports.
- Pin types: 74HC595 3-state outputs typed `output` (run 2, 8 pins) and its serial output, which OE does not gate,
  typed `tri_state` (run 1); STM32 `NRST`, printed `I/O`, typed `input` by both runs; CP2102N `RI/CLK` (an input and an
  output on one pin) typed `input`, and TPS54202 `BOOT`, printed `O`, typed `power_out`.
- Names: CP2102N `RI / CLK` kept as one name instead of `RI` with alternate `CLK`; STM32 `VDD/VDDA` split into a name and
  an `alt_names` entry although VDDA is a supply, not an alternate function.
- Package: one TPS54202 run wrote family `SOP` for a SOT-23-6, which made the build produce a footprint.
- Letter-coded outline tables: both 74HC595 runs took `L` (body to tip) for `lead_length` instead of `Lp` (the foot);
  one TXS0108E run recorded the lead centreline span as `overall_width`.

The skill was tightened for units, 3-state outputs, family names, letter-coded tables, figure-versus-table names and
`overall_width`. The `NRST` mistake is not a skill gap: the table prints `I/O` and the skill already maps that to
`bidirectional`.

### What the round found in the tool

- The footprint pitch, land-span and lead-coverage checks decided which edge a pad sits on by comparing against the
  largest coordinate, so any dual-row package whose rows are longer than half the row spacing (a TSSOP-20 at 0.65 mm)
  failed a correct footprint. Both TXS0108E runs reported it as a checker bug and left the datasheet values alone. Fixed.
- SOT-23-6 was unsupported although it is two equal rows; even-pin SOT-23 and TSOT-23 now generate footprints named as
  KiCad names them (`SOT-23-6`). Odd pin counts and other SOT packages (SOT-223, SOT-89) are still skipped.
- A Microchip MCP23017 datasheet (DS20001952C) was dropped before the round: its package drawings are vector graphics
  with no text layer, so no dimension can be quoted and the quote check cannot confirm anything. Datasheets like this need
  another way to cite a value.

### Read these numbers with care

- Eight parts, two runs each, one model. It shows where extraction breaks, not an accuracy rate.
- The gold was written by the same model that was graded and has not been reviewed by a human; the orchestrator's
  adjudication is also a model's judgement.
- The skill now uses several of these parts as examples, so the next honest test again needs datasheets that were used to
  write neither.
- "Quotes not on page" is measured with the validator in the loop, as in round 1.
