# ADS1015IDGSR (TI ADS1015, DGS VSSOP-10) — gold review

Datasheet: `ads1015.pdf`, SHA-256 `4617aa3843b16d23264f5eff63b90b1afffefff7af97ae29f0eb8c5a153156d4`,
**SBAS473F – MAY 2009 – REVISED JANUARY 2025** (Rev. F). Package drawing **DGS0010A** (page 47), land pattern page 48.
Pin configuration Figure 5-2 and Table 5-1 on page 3.

MPN taken as `ADS1015IDGSR`, the orderable part the datasheet itself prints. The PACKAGE OPTION ADDENDUM on
page 39 lists it as "ADS1015IDGSR  Active  Production  VSSOP (DGS) | 10  2500  LARGE T&R", and the same part
number recurs unsuffixed in the orderable tables on pages 41 and 42. The package-only form `ADS1015IDGS`
(which KiCad also uses as its symbol name) was rejected: that exact string is printed on no page of this
datasheet, and `skills/partspec/SKILL.md` forbids filling a value the datasheet does not state — "if the
datasheet in front of you does not state it, leave it out and say so". `reference.md` defines `mpn` as the
manufacturer part number as it should appear in KiCad, and the manufacturer part number the datasheet states is
`ADS1015IDGSR` (its `.A` and `.B` taped-and-reeled grade variants on the same page 39 row are grade suffixes,
not separate orderables). `ADS1015IDGST` is the same part in the other packing (small T&R, 250 units), and the
existence of that `IDGS`+`R`/`T` stem is why the package-only `IDGS` was tempting; the large T&R orderable is
the one recorded here.

## Cross-check against the official KiCad library

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| 1 | Pin 2 `ALERT/RDY` electrical type | Table 5-1 TYPE = "Digital output", description "**Open-drain output.** Connect to VDD using a pullup resistor." | `output` (`Analog_ADC.kicad_sym`, `ADS1015IDGS`) | **Datasheet wins.** Gold = `open_collector`, status `inferred`. The pin is open-drain: it needs a pull-up and can only pull low, so `output` understates the electrical behaviour. | 3 |
| 2 | Package family name | Cover page package table: "DGS (**VSSOP**, 10)"; drawing DGS0010A titled "**VSSOP** - 1.1 mm max height"; MO-187 variation BA | Symbol's Footprint property is `Package_SO:**TSSOP**-10_3x3mm_P0.5mm` | **Datasheet wins.** Gold `family` = `VSSOP`. Note this is a naming dispute only: KiCad's `TSSOP-10_3x3mm_P0.5mm` and its own `VSSOP-10_3x3mm_P0.5mm` are geometrically identical (verified pad-for-pad below). | 1, 47 |

Everything else agrees exactly.

### Symbol pins — 10/10 name and number matches

Datasheet Table 5-1 (ADS1015 column) and Figure 5-2, confirmed by eye on the rendered page 3:

| # | Name (gold = datasheet) | Gold type | KiCad type | Agree |
|---|---|---|---|---|
| 1 | `ADDR` | `input` | `input` | yes |
| 2 | `ALERT/RDY` | `open_collector` | `output` | **no** (row 1) |
| 3 | `GND` | `power_in` | `power_in` | yes |
| 4 | `AIN0` | `input` | `input` | yes |
| 5 | `AIN1` | `input` | `input` | yes |
| 6 | `AIN2` | `input` | `input` | yes |
| 7 | `AIN3` | `input` | `input` | yes |
| 8 | `VDD` | `power_in` | `power_in` | yes |
| 9 | `SDA` | `bidirectional` | `bidirectional` | yes |
| 10 | `SCL` | `input` | `input` | yes |

The ADS1015IDGS symbol in KiCad has no `extends` — all ten pins are in the symbol itself. No NC pins: the
ADS1015 column of Table 5-1 prints "—" for `NC` (only ADS1013/ADS1014 have NC pins), so pin_count is 10 with
all ten pins assigned.

Figure 5-1 (RUG, X2QFN) has a different name/number arrangement — that is the other package and was not used;
Figure 5-2 (DYN and DGS) matches Table 5-1 exactly.

### Footprint — `Package_SO.pretty/VSSOP-10_3x3mm_P0.5mm.kicad_mod`

| Property | Datasheet (DGS0010A) | KiCad | Agree |
|---|---|---|---|
| pad count | 10 (`10X (1.45)`, `10X (0.3)`) | 10 | yes |
| pitch | 0.5 (`8X (0.5)`) | 0.5 (y = −1, −0.5, 0, 0.5, 1) | yes |
| land span | (4.4) | pad x = ±2.2 | yes |
| land pad length × width | 1.45 × 0.3 | 1.45 × 0.3 | yes |
| body | 2.9–3.1 × 2.9–3.1 (nom 3.0) | 3x3 mm body, courtyard ±1.61 | yes |
| lead span (tip to tip) | 4.75–5.05 TYP | not recorded by KiCad | n/a |
| height | 1.1 MAX | not recorded by KiCad | n/a |

The build output `VSSOP-10_3.0x3.0mm_P0.5mm.kicad_mod` is pad-for-pad identical to KiCad's footprint
(pads 1.45 × 0.3 at x = ±2.2, y = −1…1).

## Values that had to be interpreted

All from page 47 (PACKAGE OUTLINE DGS0010A) unless stated. Every one was checked on the rendered page at
150 and 600 dpi, not only in the text layer.

1. **`overall_width` = 4.75–5.05.** The `5.05 / 4.75 TYP` stacked pair sits at the top of the top view and its
   arrow runs from the left lead tips to the right lead tips, i.e. it is the largest across-the-rows dimension,
   not a body dimension. Taken as `overall_width` per the skill's dual-row rule; the body (2.9–3.1) is separate.
   Both numbers carry `TYP`; the pair is still a min/max pair, so min/max were recorded.
2. **`body_length` = 2.9–3.1 and `body_width` = 2.9–3.1.** The outline prints `3.1 / 2.9` twice: once against
   datum feature **A** (spanning the body along the pin rows, carrying NOTE 3 "does not include mold flash") and
   once against **B** (spanning the body across the rows, carrying NOTE 4 "does not include interlead flash").
   Interlead flash is by definition the flash between two leads, i.e. on the across-the-rows face, so **B** is
   `body_width` and **A** is `body_length`. Both carry the same numbers, so the assignment does not change the
   generated footprint, but it fixes which quote belongs to which name. The text layer interleaves these with the
   `0.1 C A B` feature-control frame and `1.1 MAX`, hence the long quotes.
3. **`standoff` = 0.05–0.15 (status `inferred`).** In DETAIL A the `0.15 / 0.05` arrow runs from the extension
   line of the **body underside** down to the **seating plane** — confirmed by zooming to 600 dpi, where the
   upper extension line is level with the bottom face of the moulded body and the lower one is the lead foot's
   seating line. That is exactly the skill's definition of standoff, but the drawing never spells it out, so it
   is marked `inferred`.
4. **`lead_length` = 0.4–0.7 (status `inferred`).** The horizontal `0.7 / 0.4` arrow in DETAIL A measures the
   flat foot that rests on the board (left toe to the start of the bend), which is the skill's `lead_length`
   (the Nexperia `Lp` / ST `L` part, not the body-to-tip length). DETAIL A is captioned "TYPICAL"; the skill
   allows reference values, so the range was kept and marked `inferred`.
5. **`lead_width` = 0.17–0.27.** `10X 0.27 / 0.17` is dimensioned in the **top** view with a vertical arrow
   across one lead, i.e. the lead's width, not its length. Checked against the side view: the corresponding
   horizontal measure there is the foot length, already recorded as `lead_length`.
6. **`lead_thickness` = 0.13–0.23.** The `0.23` / `0.13` pair in the side view is dimensioned with a vertical
   arrow across the lead material at the end of the lead. Both stacked numbers are individually suffixed `TYP`
   in the drawing, but they are a stacked min/max pair, so min/max were recorded (the skill's stacked-pair rule).
   The `0.15 / 0.05` in DETAIL A was **not** used here — that is the standoff/foot-to-body gap (item 3).
7. **`pitch` = 0.5.** `8X 0.5`, boxed (basic dimension). Also printed as `8X (0.5)` in the land pattern;
   the outline value is cited.
8. **`height` = max 1.1.** `1.1 MAX`, from the side view in the feature-control frame row; it matches the drawing
   title "VSSOP - 1.1 mm max height".
9. **`land_pad_length` = 1.45, `land_pad_width` = 0.3, `land_span` = 4.4** (page 48, LAND PATTERN EXAMPLE).
   In that view the pads are drawn as horizontal rectangles, so the horizontal `10X (1.45)` is the pad's size
   along the lead direction (`land_pad_length`) and the vertical `10X (0.3)` is across (`land_pad_width`). The
   `(4.4)` dimension runs between the two pad-row centrelines, so `land_span`. All three are in parentheses,
   i.e. reference values, recorded as `nom`.
10. **Left out on purpose** (the drawing does not make them clear, or they are not in the name list):
    `2X 2` (the outermost-lead-to-outermost-lead span per row, 4 pitches = 2.0 mm — a lead centre-to-centre
    span, which the skill says not to record); `0.1 C` (positional tolerance of the seating-plane datum C);
    `0.25 GAGE PLANE`, `0° - 8°` (lead coplanarity angle), `R0.05 TYP` (lead corner radius), `PIN 1 ID AREA`;
    the solder-mask `0.05 MAX / 0.05 MIN ALL AROUND` notes; and the stencil design on page 49 (paste, not land).
    No `body_thickness` is given: the outline has no separate body-height dimension, only the 1.1 mm overall.
11. **No `group` on any pin.** The part has one MUX and one comparator, not repeated identical blocks; the
    skill's `group` is for repeated units, so it is omitted (the ADS1015 also has two identical supply pins
    that are not a "power" unit block).

### Pin types — how each was chosen (page 3, Table 5-1)

- `ADDR`, `SCL` — TYPE column "Digital input" → `input`, `extracted`.
- `SDA` — TYPE column "Digital I/O", description "Serial data input and output" → `bidirectional`, `extracted`.
- `AIN0`…`AIN3` — TYPE column "Analog input" → `input`, `extracted`. (The skill's "ADC input channel" rule
  would give `input` even with no direction printed; here a direction *is* printed, so `extracted` is honest.)
- `GND`, `VDD` — TYPE column "Analog", descriptions "Ground" / "Power supply". A supply/ground pin is
  `power_in` per the skill's table even though the I/O column is not "I" → `inferred`.
- `ALERT/RDY` — "Digital output" + "Open-drain output" → `open_collector`, `inferred` (the open-drain row of
  the skill's table is always `inferred`).

## Self-contradictions in the datasheet

None found. Three things that look like contradictions but are not:

1. **Cover page "DGS (VSSOP, 10) 3mm × 4.9mm"** vs the outline's 2.9–3.1 mm body and 4.75–5.05 mm tip-to-tip.
   The cover page's own footnote (2) says the package size is a nominal value **and includes pins**. 3 mm is the
   nominal body (mid of 2.9–3.1) and 4.9 mm is the nominal of the `5.05 / 4.75 TYP` lead-span pair. Consistent.
2. **Table 5-1 is shared by three parts** (ADS1013/1014/1015) and lists `NC` pins that only the other two
   have. The ADS1015 column prints "—" for NC, which is why this gold has no `no_connect` pin.
3. **Figure 5-1 (RUG) shows a pin arrangement different from Table 5-1**, because the X2QFN puts AIN1 on pin 5
   facing the bottom edge and rotates SCL/SDA. Figure 5-2 (DYN and DGS) matches Table 5-1 row for row, and it
   is Figure 5-2 that was used.

## Build result

`kicad-partspec validate` passes with no failures (5 `status.inferred` warnings, expected).
`kicad-partspec build` produces `out/ADS1015IDGS.kicad_sym` and
`out/partspec.pretty/VSSOP-10_3.0x3.0mm_P0.5mm.kicad_mod` — **a footprint is generated**, because the datasheet
does give a land pattern (page 48).
