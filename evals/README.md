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
| `ads1015_vssop10` | TI ADS1015 | VSSOP-10 (DGS0010A) | round 5; open-drain output |
| `drv8871_soic8` | TI DRV8871 | SOIC-8 (DDA0008B), exposed pad | round 5; `PWR` supply block |
| `mcp23008_soic18` | Microchip MCP23008 | SOIC-18 wide (C04-051D) | round 5; one datasheet for two parts |
| `sn74lvc2t45_vssop8` | TI SN74LVC2T45 | VSSOP-8 (DCU0008A) | round 5 |
| `tlc555_soic8` | TI TLC555 | SOIC-8 (D0008A) | round 5; single timer |
| `ne555_soic8` | TI NE555 | SOIC-8 (D0008A) | round 4; two lead dimensions adjudicated |
| `uln2003a_tssop16` | TI ULN2003A | TSSOP-16 (PW0016A) | round 4; seven Darlington channels grouped |
| `tca9548a_tssop24` | TI TCA9548A | TSSOP-24 (PW0024A) | round 4; eight I2C channels grouped |
| `tps5430_soic8` | TI TPS5430 | SOIC-8 PowerPAD (DDA0008B) | round 4; exposed pad `DAP` |

Round 4 ran seven parts. `ina226_vssop10`, `pca9306_vssop8` and `24lc256_soic8` had only `GOLD` verdicts, so their
golds needed no correction and were imported unchanged.

## Status of these cases

They were assembled by Claude from the datasheet text, with the mechanical drawings and pinouts
checked against rendered page images, and every value carries a page and a verbatim quote that the
source-layer check re-verifies. **No human has compared them with the datasheets**, and nothing in
this repository substitutes for one: the golds are drafts whose entire audit trail is the checks
described in this file — the rendered-page reads, the quote check, the cross-check against the
official KiCad library, and each round's adjudication — plus the gold errors those checks caught
after the fact, listed per round below. Where a contested reading had no rule behind it, the rule was
written into `skills/partspec/reference.md` rather than left for a reader to re-decide.

The round-2, round-4 and round-5 cases were also cross-checked against the official KiCad library symbol and footprint; each case's `review.md` lists every disagreement with KiCad and how it was decided. Reading the disagreements with the extraction runs afterwards still found two gold errors in round 2, four in round 4 and five in round 5, so the golds are model-derived drafts whose checks are the ones described here and nothing more.

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
- Where a gold leaves a dimension out, its own `review.md` says why; nothing is dropped here as a blanket rule, and a
  convention in this file is never a rule an extraction run is graded against. The golds carry the values the datasheets
  support — the TLC555 gold once omitted `standoff` and `lead_thickness` on the strength of an ambiguity note in this
  section, which round 5's adjudication overruled: p. 38 prints "SEATING PLANE" and DETAIL A's arrows decide both.
- In round 4 the NE555 D0008A gold records both of the sheet's SOIC callouts: the front-view lead-toe callout as
  `lead_thickness` and DETAIL A's body-underside-to-seating-plane callout as `standoff`. The adjudication marked the
  `standoff` its lower-confidence item because the callout resolves only at 600 dpi; re-rendered at 600 dpi during the
  merge the extension lines decide it — body underside to the dashed seating line — so it is recorded. The rule that
  settles it: a callout is named by what its extension lines decide, at whatever dpi that takes, and only a callout that
  stays illegible even at high dpi is left out; the old blanket rule that left these SOIC callouts out is withdrawn.

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

Seven parts that were used to write neither the skill nor an earlier gold, two runs each — 14 runs. The round's own
verdicts, row by row, are in `runs/round4_adjudication.md`.

How it was run:

- Each run started in an empty directory holding only the datasheet PDF, with the plugin loaded from this repository
  (`claude --plugin-dir`, so the skill and the MCP server as a user gets them), headless, told to finish without asking,
  and with the CLI validator in the loop.
- Skill version: the skill as round 2 left it (commit `21e827b`, "Tighten the extraction skill after evaluation round 2").
  Nothing in `skills/` changed between round 2's runs and these: both skill changes this round produced came afterwards,
  from its own results.
- Model: the same non-Claude model as round 2, through the same OpenCode Go launcher; the run logs name it
  `space-bunny`, where round 2 recorded `space-bunny-free`. Round 1 used a Claude model, so round 1 is not comparable
  with the other two, and rounds 2 and 4 share a model family but not a named model.
- Isolation by ordering, not by instruction: a case's gold was written only after both of its runs had finished, and the
  gold author was told not to read the runs directory.
- Gold: written by a separate run with every pin and dimension confirmed on a rendered page, then cross-checked against
  the official KiCad symbol and footprint (`cases/<case>/review.md` records every disagreement with KiCad).
- Adjudication: a separate model session re-decided every scorer disagreement against the PDF, page by page
  (`runs/round4_adjudication.md`; it refers to `score_output.txt`, the round's scorer output, whose content is the `types`,
  `dims` and `usable` columns of the first table below). Its gold corrections were then applied and independently
  spot-checked by eight verification workers, each confirming that the fix fails on the previous commit and passes here.
- The three cases whose gold needed no correction (`24lc256_soic8`, `ina226_vssop10`, `pca9306_vssop8`) are imported
  unchanged, so all seven cases are in `cases/`. `runs/round4_scores.json` was taken after that import and scores all 14
  runs against these golds, quotes included: the eight runs of the corrected cases score as the round's own output did —
  the two ULN2003A runs excepted, which now differ from their gold on `COM`'s group (see "What went wrong") — and the six
  runs of the imported cases were not scorable from this repository before the import.

| Run | types | dims | quotes not on page | usable as scored | usable after adjudication |
|---|---|---|---|---|---|
| 24lc256 run1 / run2 | 7/8, 7/8 | 1/1, 1/1 | 0/9, 0/9 | no, no | no, no |
| ina226 run1 / run2 | 10/10, 10/10 | 11/12, 11/12 | 0/22, 0/22 | no, no | no, no |
| ne555 run1 / run2 | 8/8, 8/8 | 8/10, 9/10 | 0/19, 0/20 | yes, yes | yes, yes |
| pca9306 run1 / run2 | 4/8, 8/8 | 11/12, 12/12 | 0/19, 0/20 | no, yes | no, yes |
| tca9548a run1 / run2 | 24/24, 24/24 | 8/11, 9/11 | 0/35, 0/35 | yes, no | no, yes |
| tps5430 run1 / run2 | 9/9, 9/9 | 11/14, 10/14 | 0/22, 0/23 | no, no | no, no |
| uln2003a run1 / run2 | 16/16, 16/16 | 8/11, 10/11 | 0/28, 0/28 | no, no | yes, yes |
| **total** | | | | **4/14** | **6/14** |

The `types`, `dims` and quotes columns are the round's own scoring, against the gold as it stood before this round's
corrections; the NE555 denominator is lower there than in `runs/round4_scores.json`, which scores the same runs against a
gold that has since gained two dimensions (`lead_thickness` and `standoff`). The last column is the same runs after each
disagreement was re-decided against the datasheet: it moves where the adjudicator found the gold at fault rather than the
run, and it moves in both directions. TCA9548A run 1 was usable as scored and is not after adjudication, because the
gold that lacked the eight channel groups was the thing that had to change; ULN2003A's two runs and TCA9548A run 2 go the
other way. 6 of 14 is not an accuracy rate either — see "Read these numbers with care".

The last column is the round's own history, and it does not survive into this repository unchanged: the golds here group
ULN2003A's common emitter `E` as `power` but leave the common cathode `COM` ungrouped (see "What went wrong"), so the two
ULN2003A runs differ from the gold on that one pin and scored against the golds as they now stand the runs are 4 of 14
usable — `runs/round4_scores.json` is that scoring — so the table's "usable" columns are properties of the round, not of
the files in `cases/`.

One datasheet ends with no footprint: the **Microchip 24LC256**. It does print a recommended land pattern (page 19,
drawing C04-2057A), but that drawing has no text layer, so not one of its numbers can be quoted and the quote check
cannot confirm any of them — the same barrier that dropped the Microchip MCP23017 before round 2. Its gold therefore
carries no `land_*` dimensions and the build reports `footprint.skipped`. The other six datasheets all have a quotable
land pattern, and the only runs whose generated footprint differed from their gold's are the two TPS5430 runs, both on
real dimension errors (below).

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

Every run found every pin and no run invented a pin, a pin number or a name. Every quote in every run was on the page it
was cited to. All 14 runs got the package family and pin count right.

### What went wrong

Grouped by kind, from `runs/round4_adjudication.md`. "Run" means the run was right and the gold had to change; those rows
are the subject of the next section.

- **Units.** All four runs of the two parts built from repeated blocks grouped them: ULN2003A's seven Darlington channels
  keyed `1`…`7` and its common emitter and cathode `power`, TCA9548A's eight I²C channels keyed `CH0`…`CH7` with its
  ground and supply `power`. Two golds omitted those groups entirely — 17 and 18 run-verdict rows. The merged golds took
  the channel keys and grouped the common rails `power`, except ULN2003A's common cathode `COM`: the datasheet's own
  power-supply text says the device needs no supply and that COM may float, so it stays `passive` and ungrouped while the
  emitter `E`, "typically tied to ground", takes `power`. `reference.md` carries that carve-out as a rule.
- **Pin types.** PCA9306 run 1 typed the four open-drain bus pins `open_collector` where the pin table's TYPE column
  prints `I/O`; the phrase "Open-drain I2C I/O ports" describes the external bus, and the word appears nowhere in the
  pin table. Both 24LC256 runs typed SDA `open_collector` where §2.2 calls the pin "**bidirectional**" and only the
  terminal open-drain. Nothing else was mistyped: types are 8/8, 10/10, 24/24, 9/9 and 16/16 on the other five parts.
- **Names.** TPS5430 run 2 named pin 9 `EP`, the generic word `reference.md` uses in its `alt_names` example; TI prints
  `DAP` on both the pin table and the package drawing.
- **Which page is in use.** One TPS5430 run took the exposed-pad size from the superseded `DDA0008J` package drawing
  elsewhere in the same datasheet; the page in use prints `2.71` over `2.11`, far enough apart to move the generated
  footprint.
- **Stacked pairs.** On a TI sheet, `7.9 / 7.7`, `4.5 / 4.3` and `0.30 / 0.19` under one callout are max over min, read
  top-down, not a nominal and a maximum. One TCA9548A run swapped `overall_width` with `body_length` over the same pair
  shape; the other read `6.6` over `6.2 TYP` as `nom 6.6 / max 6.6`.
- **The three DETAIL A callouts.** One NE555 run reused the lead thickness as the standoff; one TCA9548A run put the lead
  length there; the other NE555 run kept only the upper limit of the standoff as a nominal. The same three names were read
  three ways on one round, which is why the skill now says which two planes each span.
- **A dropped limit.** One ULN2003A run recorded `lead_width` and `standoff` with their lower limits only.
- **Left out that should be there.** NE555 run 1 dropped `lead_length`, a callout the sheet plainly gives (`.016-.050
  [0.41-1.27]`); PCA9306 run 1 dropped `lead_thickness`, `(0.13) TYP` in the side view.

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
independent evidence about the runs, and `## Status of these cases` already says the golds are model-derived drafts.

### What the round found in the tool

No defect in this repository's code: every fix this round went into a gold or into `skills/partspec/reference.md`. Round
2's two tool fixes both held. The footprint pitch, land-span and lead-coverage checks, which round 2 had to repair because
they decided which edge a pad sits on by comparing against the largest coordinate, handled this round's TSSOP-16 and
TSSOP-24 — the 0.65 mm dual-row family that broke them — without complaint, and 12 of the 14 runs generated a footprint
identical to their gold's.

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

### What the round says about round 2's changes

Round 2 ended by tightening the skill in six places. This round is the first test of that edit, and the six split three
ways.

Two held outright. `package.family`: all 14 runs named the package family correctly, after round 2 lost a run to `SOP`
for a SOT-23-6. The letter-coded outline table for Nexperia, NXP and ST was simply not exercised — all seven parts are
TI or Microchip, every outline prints names rather than letters — and neither was the 3-state output rule, since no part
here has a high-impedance state. Untested is not passed.

One was right and was still got wrong. Round 2 said `overall_width` is the largest across-rows dimension on the outline
and that a lead centre-to-centre span is not recorded; one NE555 run recorded the `2X .150 [3.81]` centreline span there
anyway. The rule it needed was about the sheet, not the span, and the skill still has none — see below.

One needed rewriting rather than defending. Round 2's `group` rule gave the examples `"A"`, `"B"` and the supply pins
`"power"`, and all four runs of the multi-channel parts used it correctly, including the clause that a unit's two pins
share one key (ULN2003A keyed `1B` and `1C` together) and the clause that two banks of a memory are not two units. The
three golds that avoided grouping did so because nothing in the rule said a numbered channel is a channel. Rewritten, as
described above.

### Two readings the skill still does not cover

Both recur across the dimension rows, on the runs and on the golds, and neither has a rule in `reference.md`.

The first is **which page is in use**. One TPS5430 run took the exposed-pad size from the superseded `DDA0008J` package
drawing elsewhere in the same datasheet; the page actually in use prints `2.71` over `2.11`, and the two differ enough to
move the generated footprint. The same datasheet has two dimensions that look like the exposed pad — `(2.71)`/`(3.4)` on
the solid green "solder mask defined pad" and `(2.95)`/`(4.9)` on the dashed "metal covered by solder mask" outline —
and only the first is the pad.

The second is **stacked pairs**. On a TI sheet, `7.9 / 7.7`, `4.5 / 4.3` and `0.30 / 0.19` printed under one callout are
max over min, read top-down — not a nominal and a maximum. Most of the dimension rows in the contested-row table above are
of this kind, and two golds read `overall_width` the wrong way round the same way (`6.6` over `6.2 TYP`, `6.2` over
`5.8`). `SKILL.md` says to record a value the datasheet gives only as a range as `min`/`max`, which is the right rule,
but it does not say how to recognise the pair once it is on the page, and nothing in the skill says to check that the
revision note under the drawing does not supersede the drawing.

### Read these numbers with care

- Seven parts, two runs each. It shows where extraction breaks, not an accuracy rate.
- The gold was written by the same model that was graded, cross-checked against KiCad but not reviewed by a human,
  and four of its seven cases were corrected after the runs were scored. The corrected gold is not independent of the
  runs, and both the 4-of-14 as scored and the 6-of-14 after adjudication are properties of that combination. The
  second figure is not the better one: it counts a run as usable once the answer key has been rewritten to agree with
  it.
- Adjudication was done by a model reading the same PDFs, then spot-checked by eight verification workers who confirmed
  the fixes rather than re-deriving every row. It is a model's judgement with a model's second opinion, not a human one.
- `runs/round4_scores.json` covers all 14 runs against the golds in `cases/`, taken after the import with the datasheets
  at hand for the quote check. Before the import the six runs of the three no-correction cases had no gold in this
  repository to score against, and the round's own scoring of the other eight was taken when their golds lived outside.
- The rounds are not comparable to each other: round 1 ran before the skill was tightened by round 1's own results,
  round 2 ran with a different model, and this round's results have since been folded into the skill as well.
- "Quotes not on page" is measured with the validator in the loop, as in rounds 1 and 2.
## Extraction round 5

Five parts from three vendors, two runs each, none of them used to write the skill or any gold. Outputs are in
`runs/round5/`, scores in `runs/round5_scores.json`, the full adjudication in `runs/round5_adjudication.md`; reproduce
with `python evals/score.py --extracted evals/runs/round5 --datasheets DIR`.

How it was run:

- Each run started in an empty directory holding only the datasheet PDF, with the plugin loaded from this repository
  (`claude --plugin-dir`, so the skill and the MCP server as a user gets them), headless, told to finish without asking.
- Model: `space-bunny` through OpenCode Go for every run and every gold author — the successor of the `space-bunny-free`
  round 2 used, and not a Claude model. The skill and the harness are otherwise identical to round 2, so the model string
  is the only thing that changed between the two rounds' numbers.
- Skill version: the plugin snapshot is this repository's `skills/` and `.claude-plugin/` as of `93941cd`, the round-2
  SOT-23 commit, byte for byte. **The skill has not changed since round 2**, so round 5 measured the rules round 2
  measured, not a revised set; everything the round changed in the skill came afterwards.
- Isolation by ordering, not by instruction: a case's gold was written only after both of its runs had finished.
- Gold: written by a separate run with every pin and dimension checked on a rendered page, then cross-checked against the
  official KiCad symbol and footprint. The KiCad symbol, library and footprint each case was checked against are recorded
  in the round's case list and asserted by `tests/test_symbol.py`, which compares every gold pin number and name to the
  installed library and passes for all five cases. As in round 2, no human has read them.
- Adjudication: one model per case, working from the PDF text and a 150 dpi render of the cited page, deciding every
  disagreement against `SKILL.md` and `reference.md` with one of four verdicts (**GOLD** gold right, **RUN** run right,
  **BOTH** either is permitted, **NEITHER** both wrong). The per-case files are concatenated verbatim in
  `runs/round5_adjudication.md` and were spot-checked while this section was written. Grand tally: **GOLD 28 · RUN 9 ·
  BOTH 6 · NEITHER 0** over 40 scored items, plus three gold errors the scorer could not see because both runs agreed
  with the gold. All corrections are applied to the gold files here, and the table below is scored against the corrected
  gold.
- Every one of the five datasheets prints an example land pattern, so every case has a footprint; none was skipped.

| Run | types | dims | quotes not on page | usable as scored | usable after adjudication |
|---|---|---|---|---|---|
| ads1015 run1 / run2 | 10/10, 10/10 | 9/12, 11/12 | 0/22, 0/22 | no, yes | no, yes |
| drv8871 run1 / run2 | 9/9, 9/9 | 11/14, 12/14 | 0/22, 0/23 | no, no | no, no |
| mcp23008 run1 / run2 | 18/18, 18/18 | 11/13, 12/13 | 0/31, 0/31 | no, no | no, no |
| sn74lvc2t45 run1 / run2 | 8/8, 8/8 | 9/12, 5/12 | 0/19, 0/17 | yes, yes | yes, yes |
| tlc555 run1 / run2 | 8/8, 8/8 | 11/12, 9/12 | 0/19, 0/20 | yes, no | yes, no |
| **total** | | | | **4/10** | **4/10** |

"Usable" is the scorer's own definition: the generated symbol and footprint are identical to the gold's and every quote
is on its page. A wrong dimension that neither file uses does not disqualify a run, which is why SN74LVC2T45 run 2 counts
with five of twelve dimensions right. Adjudication moved nothing in this column — every RUN and BOTH verdict belonged to a
run that had already failed on something the adjudication upheld — but it did move five gold fields and three gold status
labels onto the runs' side, without which DRV8871 run 1's symbol and TLC555 run 1's dimensions would have been marked wrong
on the gold's error rather than on the run's own.

### What went wrong

Grouped by kind, from the adjudication. Pin **types** were the one thing that went right: 106 of 106 pin types across the
ten runs, and every run found every pin, with no invented pin, number or name.

- **Which axis a callout runs along** — the dominant failure, and it is the same failure wherever it appears. ADS1015
  run 1 swapped `body_length` and `overall_width`; SN74LVC2T45 run 2 rotated `overall_width`, `body_width` and
  `body_length` onto the wrong axes and moved the seating-plane value to `standoff`; TLC555 run 2 took the body-face-to-tip
  callout — the one the rules explicitly exclude — as `lead_length`; MCP23008 run 2 filed the moulded-body dimension `D`
  as `overall_length`, a span the drawing does not print at all.
- **A boxed basic or a `GAGE PLANE` callout read as a size** — ADS1015 run 1 took `0.25 GAGE PLANE` for both
  `lead_length` and `standoff`; TLC555 run 2 took the `⌖ C A B` coplanarity tolerance as `lead_thickness`; SN74LVC2T45
  run 1 put DETAIL A's horizontal foot callout under `lead_thickness` and lost `lead_length` for it.
- **Mask against metal** — DRV8871 took the `(2.71)` "SOLDER MASK OPENING" rectangle as `land_ep_size` where the copper pad
  is `(2.95)` "METAL COVERED BY SOLDER MASK" (both runs). The two DRV8871 runs and MCP23008 run 2 are the only three runs
  whose generated footprint differs from the gold's; the other two are the axis errors above.
- **`nom` against `max` on a land table** — MCP23008 run 1 recorded both single-value land rows as `max` where the gold,
  and the land-pattern rule, say `nom`.
- **A name from another part in the same datasheet** — MCP23008 run 2 took `SCK`, `SI`, `SO` and `CS` out of cells that
  pair the MCP23008 pad with the MCP23S08 name, as alternate functions of this part. ADS1015 run 1 split the printed
  token `ALERT/RDY` and kept `RDY` as an alternate function.
- **Grouping the supply pins** — the only systematic disagreement, and it is a rules defect rather than a reading error.
  `reference.md` listed `power` as a group value inside a bullet gated on "repeated, identical functional blocks", so
  five runs split: DRV8871 run 1 grouped its three `PWR` pins and the pad (verdict RUN, the gold corrected to match),
  MCP23008 both runs grouped VDD/VSS (BOTH), TLC555 run 2 left GND/VDD ungrouped (BOTH), and ADS1015 run 1 grouped the
  two supply pins (BOTH).
- **The gold's own errors**, found by the adjudicators on a full read rather than from the score: ADS1015's `mpn` was
  `ADS1015IDGS`, a KiCad-side package-only string no page prints (both runs were right); MCP23008's pin 6 was `RESET`
  where the datasheet overbars it and the rules ask for `RESET-`; TLC555 omitted `standoff` and `lead_thickness` on the
  strength of a note in this file's "Conventions", which round 5 overruled.
- Nothing else. No run invented a package family — all ten produced a family the tool builds — and no run raised a
  checker complaint, the two tool bugs round 2 found having stayed fixed.

### What the round says about the previous round's skill changes

Round 2 closed six skill gaps and two tool gaps. Two of the six held cleanly on parts that exercised them: SN74LVC2T45 is
a two-port level translator and neither run invented units out of the two ports, and all ten runs named a package family
the tool builds. Two were not exercised again — no round-5 part has 3-state outputs, and none has a figure name that
disagrees with its table. Two did not close: the letter-coded outline table (round 2's `L` versus `Lp`) and
`overall_width`. Every one of these five cases has letter- or datum-coded outline callouts (`NOTE 3`, `D` against `E`,
`SEATING PLANE`, `GAGE PLANE`), and they produced most of the dimension errors. What neither round's rule says — and what
this round showed no run could guess — is that a callout is named by where its extension lines land and which way its
arrow runs; that is the question nearly every one of those errors turns on. The round-2 wording did give the adjudicators
a shared vocabulary for settling them. The two tool gaps stayed closed: no pitch, land-span or lead-coverage check failed a
correct result, and the SOT-23 support had nothing to bite on.

The skill was then tightened for what this round did find — `mpn` as the datasheet prints it; `power` un-gated from the
"identical blocks" rule; `alt_names` from this part only; naming each callout by its extension lines on the render; a
boxed basic or `GAGE PLANE` callout is a datum and never a size; the body-face-to-tip exclusion for any vendor; `land_*`
from the metal rectangle; and this file's convention that called two SOIC callouts ambiguous withdrawn, since a
convention here is not a rule a run is graded against. No code changed.

### Read these numbers with care

- Five parts, two runs each, one model. It shows where extraction breaks, not an accuracy rate.
- The skill is the round-2 skill and the gold was written by the same model that was graded; neither has been reviewed by
  a human. The adjudication is a model's judgement on a rendered page, spot-checked while this section was written, not
  a second opinion from one.
- The tally reads GOLD 28 · RUN 9, and the nine are not independent noise: four are the `group` contradiction on the
  DRV8871's `PWR` pins, two are the TLC555 callouts this file's own convention had written off, and one each is the `mpn`
  definition, the polarity convention and a `status` label. Nine items, three rules. Forty items is not forty facts.
- Half the round turned on three questions — which axis the callout runs along, whether a boxed value is a size, and
  whether a rectangle is metal or mask — so the per-item counts overstate how many separate things went wrong.
- The table is scored against a gold that nine adjudicated verdicts moved: five fields and three status labels were
  changed to match the runs. The moves were all towards the runs, and they were made by the process that graded them.
- "Quotes not on page" is measured with the validator in the loop, as in rounds 1 and 2. It is not a first-attempt rate.
- Round 4 was run on this same harness and this same skill and is written up above, its golds now in `cases/`; round 3's
  data is not in this repository, so the documented rounds are not a continuous series.
