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
| `ne555_soic8` | TI NE555 | SOIC-8 (D0008A) | round 4; two lead dimensions adjudicated |
| `uln2003a_tssop16` | TI ULN2003A | TSSOP-16 (PW0016A) | round 4; seven Darlington channels grouped |
| `tca9548a_tssop24` | TI TCA9548A | TSSOP-24 (PW0024A) | round 4; eight I2C channels grouped |
| `tps5430_soic8` | TI TPS5430 | SOIC-8 PowerPAD (DDA0008B) | round 4; exposed pad `DAP` |

Round 4 ran seven parts. The three above that are not listed — `ina226_vssop10`, `pca9306_vssop8` and
`24lc256_soic8` — needed no correction to their gold, so they are not imported here.

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
- A SOIC/TQFP callout that does not resolve is left out rather than guessed. The SOIC `.004-.010` and
  `.005-.010` values were such a case. In round 4 the NE555 D0008A gold records both: `.005-.010` (front view,
  across the lead toe) as `lead_thickness`, unambiguous at 150 dpi, and `.004-.010` (DETAIL A, body underside to
  seating plane) as `standoff`, which only resolves at 600 dpi. The adjudication flagged the `standoff` as its
  lower-confidence item and said a human should decide whether to override this convention; **that decision is
  still open**. Below the dpi where the extension lines are legible, leave them out as before.

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

## Extraction round 4

Seven parts that were used to write neither the skill nor an earlier gold, two runs each — 14 runs. Every run got the
plugin as a user gets it, headless, with nothing but the datasheet PDF in its directory. Golds were written with every
pin and dimension checked on a rendered page and then cross-checked against the official KiCad symbol and footprint
(`cases/<case>/review.md`); every run-versus-gold disagreement was then re-decided against the PDF by the
orchestrating session, page by page.

| Case | runs | contested rows | gold | run | neither |
|---|---|---|---|---|---|
| ne555_soic8 | 2 | 5 | 3 | 1 | 1 |
| 24lc256_soic8 | 2 | 3 | 3 | 0 | 0 |
| ina226_vssop10 | 2 | 3 | 3 | 0 | 0 |
| pca9306_vssop8 | 2 | 5 | 5 | 0 | 0 |
| tca9548a_tssop24 | 2 | 23 | 3 | 18 | 2 |
| uln2003a_tssop16 | 2 | 20 | 3 | 17 | 0 |
| tps5430_soic8 | 2 | 5 | 4 | 1 | 0 |
| **total** | **14** | **64** | **24** | **37** | **3** |

Scored as the rounds before it, 4 of the 14 runs came out usable without edit: both NE555 runs, PCA9306 run 2 and
TCA9548A run 1. No run invented a pin or a pin number, every run found every pin, and every quote in every run was on
the page it was cited to.

### What the round found in the golds

The interesting result is the other column. In 40 of the 64 contested rows — the 37 `RUN` verdicts and the 3
`NEITHER` ones, where the run was right or both sides were wrong — the gold was the thing that had to change; the
24 `GOLD` rows are where the gold held and the run misread the page. Three classes of error account for most of it:

- Two golds — ULN2003A and TCA9548A — recorded a part built from repeated identical blocks (seven Darlington pairs,
  eight I²C channels) as having no units at all, because the datasheet numbers the channels inside the pin names
  (`1B`…`7B`, `SD0`…`SD7`) instead of printing unit letters. Nothing in `SKILL.md` or `reference.md` requires letters;
  `A`/`B` appear there only as examples of keys. Both golds gained the datasheet's own channel numbers.
- Two more golds — ULN2003A and TPS5430 — read a stacked `max / min TYP` pair as `nom / max`. A nominal equal to the
  lower limit of its own range is not a reading any convention supports; the TCA9548A gold already used `min`/`max`
  for the identical `6.6 / 6.2 TYP` callout, so the three golds disagreed with each other.
- The TCA9548A gold recorded a standoff as a `lead_thickness` — the DETAIL A `0.15 / 0.05` callout, which is the same
  standoff on PW0016A and DCU0008A.

The golds that held up held up against runs that all made the same mistake: on 24LC256 and INA226 both runs invented a
`power` group for a lone supply pin, which `reference.md` says to omit. That is four gold-right rows in the table above,
and they are the one kind of disagreement this round scored cleanly — the runs were all wrong the same way.

This round's golds needed correcting too, after two gold errors in round 1 and two in round 2.
That is the argument for treating these files as a first draft: a gold corrected after the runs are seen is not
independent evidence about the runs, and `## Status of these cases` already says a human review is still needed.

### What the round found in the tool

Two rules in `skills/partspec/reference.md` were wrong or missing, and both were fixed:

- `group`. The ULN2003A and TCA9548A runs keyed their channels and the rule was ambiguous enough that the golds
  avoided it. The rule now says that repeated identical blocks are keyed by whatever the datasheet calls them —
  numbers included — and that the two sides of one unit share a key; it also names the supply pins as the `power`
  key explicitly, which both runs used correctly and neither gold allowed.
- Telling `standoff`, `lead_length` and `lead_thickness` apart. DETAIL A's `0.15 / 0.05` callout is the standoff and
  the front view's `(0.15) TYP` is the lead thickness on three TI package sheets, and the golds split between them.
  The rule is now the distinction the drawings actually make — seating plane to body underside, lead tip to start of
  bend, and the cross-section across the lead — together with the rule that a parenthesised value is a reference value:
  usable for `land_*`, not for a package limit.

### The recurring failure mode

Two readings recur across the dimension rows, and the golds got them wrong too.

The first is **which page is in use**. One TPS5430 run took the exposed-pad size from the superseded `DDA0008J`
package drawing elsewhere in the same datasheet; the page actually in use prints `2.71` over `2.11`, and the two
differ enough to move the generated footprint. The same datasheet has two dimensions that look like the exposed pad —
`(2.71)`/`(3.4)` on the solid green "solder mask defined pad" and `(2.95)`/`(4.9)` on the dashed "metal covered by
solder mask" outline — and only the first is the pad.

The second is **stacked pairs**. On a TI sheet, `7.9 / 7.7`, `4.5 / 4.3` and `0.30 / 0.19` printed under one callout
are max over min, read top-down — not a nominal and a maximum. Most of the dimension rows in the table above are of this
kind, and two golds read `overall_width` the wrong way round the same way (`6.6` over `6.2 TYP`, `6.2` over `5.8`).

### Read these numbers with care

- Seven parts, two runs each. It shows where extraction breaks, not an accuracy rate.
- The gold was written by the same model that was graded, cross-checked against KiCad but not reviewed by a human,
  and four of its seven cases were corrected after the runs were scored. The corrected gold is not independent of
  the runs, and the 4-of-14 figure above is a property of that combination.
- The rounds are not comparable to each other: round 1 ran before the skill was tightened by round 1's own results,
  round 2 ran with a different model, and this round's results have since been folded into the skill as well.
- "Quotes not on page" is measured with the validator in the loop, as in rounds 1 and 2.
