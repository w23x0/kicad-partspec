# 24LC256 (SOIC-8) — gold review

Datasheet: `24lc256.pdf`, Microchip DS20001203U, Revision U (11/2013),
sha256 `baed9ce6a87b803346305d5369c53968f32c466f28a540c9fd130dba2e144f1c`,
42 pages. The cover page names the part family; the revision is in
APPENDIX A: REVISION HISTORY (page 36), "Revision U (11/2013)".

Every pin was read from Table 2-1 (page 5), cross-checked against the
"Package Types" pinout figure on page 1, and confirmed on rendered images
(pages 1 and 5 at 150 dpi).

## The blocking finding: this datasheet has no text layer on its package drawings

Microchip's mechanical drawings (pages 16–25) are vector art with a subsetted
font whose ToUnicode map poppler cannot use. `pdftotext -layout` extracts
control characters instead of glyphs:

```
$ pdftotext -layout -f 18 -l 18 24lc256.pdf -      # SOIC dimension table page
24AA256/24LC256/24FC256
  Note:   For the most current package drawings, ...
DS20001203U-page 18        © 1998-2013 Microchip Technology Inc.
```

Only the running header, the boilerplate note and the footer survive. The
SOIC outline table (page 18), the SOIC recommended land pattern (page 19) and
the PDIP table (page 16) are all unreadable as text. A grep of the whole
42-page extraction for `1.27`, `1.75`, `5.40`, `0.60`, `0.31`, `0.17`, `0.25`
returns **zero** hits; `4.90`, `3.90` and `6.00` only ever appear inside
telephone numbers, addresses and the package name.

A PartSpec requires `source.quote` for every dimension and
`kicad-partspec validate --datasheet` (and `evals/check_gold.py`, which uses
the same `pdftotext -layout`) fails `prov.quote_not_found` for any quote that
is not on the page. **No dimension value on pages 18 or 19 can therefore be
cited honestly.** This is the same barrier that made the MCP23017 case
(DS20001952C) undeliverable; see evals/README.md, "What the round found in the
tool".

Consequence for this gold: the package outline table and the land pattern are
recorded below **for a human reviewer**, but only the one dimension the
datasheet states in extractable text (`body_width`, from the product
identification system on page 39) is in `spec.gold.json`. No dimension was
taken from KiCad or from any other document. The build consequently skips the
footprint, which is the honest outcome.

### The values that are there (page 18, drawing C04-057C sheet 2 of 2, MILLIMETERS)

| Row as printed | Value | Would be |
|---|---|---|
| Number of Pins N | 8 | — |
| Pitch e | 1.27 BSC | `pitch` nom 1.27 |
| Overall Height A | MAX 1.75 | `height` max 1.75 |
| Molded Package Thickness A2 | MIN 1.25 | `body_thickness` min 1.25 |
| Standoff § A1 | 0.10 / 0.25 | `standoff` min 0.10 max 0.25 |
| Overall Width E | 6.00 BSC | `overall_width` nom 6.0 |
| Molded Package Width E1 | 3.90 BSC | `body_width` nom 3.9 (in the gold, cited from page 39 instead) |
| Overall Length D | 4.90 BSC | `body_length` nom 4.9 — see the contradiction note below |
| Chamfer (Optional) h | 0.25 / 0.50 | not a PartSpec dimension, omit |
| Foot Length L | 0.40 / 1.27 | `lead_length` min 0.40 max 1.27 |
| Footprint L1 | 1.04 REF | reference only, omit |
| Foot Angle φ | 0° / 8° | omit |
| Lead Thickness c | 0.17 / 0.25 | `lead_thickness` min 0.17 max 0.25 |
| Lead Width b | 0.31 / 0.51 | `lead_width` min 0.31 max 0.51 |
| Mold Draft Angle Top α / Bottom β | 5° / 15° | omit |

### The recommended land pattern (page 19, drawing C04-2057A, MILLIMETERS)

| Row as printed | Value | Would be |
|---|---|---|
| Contact Pitch E | 1.27 BSC | `pitch` nom 1.27 |
| Contact Pad Spacing C | 5.40 | `land_span` nom 5.4 |
| Contact Pad Width (X8) X1 | MAX 0.60 | `land_pad_width` |
| Contact Pad Length (X8) Y1 | MAX 1.55 | `land_pad_length` |

`C` was measured centre-to-centre on the rendered page (the extension lines
run through the middle of the pads), and 5.40 is self-consistent: with 0.60
wide pads the outer span is 6.00 mm, exactly the package's overall width `E`.
If someone adds these dimensions, note that X1 and Y1 are printed in the MAX
column of a table the note calls reference values; `nom` (per the README's
"land_* dimensions are reference values, not limits") and `max` (per
reference.md's "a value marked MAX gets only max") are both defensible.

## KiCad cross-check

- Symbol: `/usr/share/kicad/symbols/Memory_EEPROM.kicad_sym`, symbol `24LC256`
  `extends "24LC16"`; the eight pins live in the parent `24LC16`.
- Footprint: `/usr/share/kicad/footprints/Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod`.

### Disagreements

| Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|
| Pin 4 name | `VSS` (Table 2-1; "Ground"). The page-1 pinout figure prints `Vss`. | `GND` | Datasheet: `VSS`. Microchip's own name for the pin, and the datasheet never uses `GND` for it. | 5 |
| Pin 5 `SDA` type | "This is a **bidirectional** pin used to transfer addresses and data into and out of the device. It is an **open drain** terminal." | `bidirectional` | `bidirectional`. The open-drain sentence describes the electrical connection, not an output direction; the skill maps open drain **outputs** to `open_collector`, and this pin is not an output. Both sources agree. | 5 |
| Land pad centre-to-centre span | `C` = 5.40 (recommended land pattern) | pad centres at x = ±2.475 → 4.95 (IPC-7351 density level) | Datasheet would win (page 19); not in the gold because page 19 has no text layer. The difference is Microchip's land pattern vs KiCad's IPC-7351 pads, not a package disagreement. | 19 |
| Land pad length | `Y1` = 1.55 (recommended land pattern) | pad size 1.95 × 0.60 | Not a disagreement: pad geometry comes from IPC-7351, not the datasheet land pattern. Pad *width* (0.60) is identical. | 19 |
| Pin 4 electrical type | "Ground" | `power_in` | Agree. | 5 |
| Pins 1–3 `A0`/`A1`/`A2` | "The A0, A1 and A2 **inputs**" (§2.1) | `input` | Agree. | 5 |
| Pin 6 `SCL` | "This **input** is used to synchronize the data transfer" (§2.3) | `input` | Agree. | 5 |
| Pin 7 `WP` | "Write-Protect Input" | `input` | Agree. | 5 |
| Pin 8 `VCC` | "+2.5V to 5.5V (24LC256)" | `power_in` | Agree. | 5 |
| Pin count | 8 (Table 2-1 SOIC column; "Number of Pins N = 8") | 8 pads | Agree. | 5, 18 |
| Pitch | `e` = 1.27 BSC | pads at y = ±1.905, ±0.635 → 1.27 | Agree. | 18 |
| Body size | 3.90 × 4.90 mm ("SOIC (3.90 mm body)", E1 3.90 BSC, D 4.90 BSC) | footprint name `SOIC-8_3.9x4.9mm`, silk at ±2.06 / ±2.56 | Agree. | 18, 39 |
| Package family | "8-Lead Plastic Small Outline (SN) – Narrow, 3.90 mm Body [SOIC]" | `SOIC*3.9x4.9mm*` footprint filter | Agree; `family` is `SOIC`. | 17 |

### Agreements that are not disagreements but are worth recording

- The page-1 "Package Types" figure prints `A0, A1, A2, Vss, Sda, Scl, WP, Vcc`
  and the page-5 table prints `A0, A1, A2, VSS, SDA, SCL, WP, VCC`. Same
  numbers, same pairing, only schematic-style capitalisation differs. The gold
  uses the table's spelling, which is also KiCad's.
- The page-1 figure puts `A0` on pin 1 and `Vcc` on pin 8 for the combined
  PDIP/SOIC/SOIJ outline, so the figure corroborates the table's SOIC column
  rather than contradicting it.

## Values I had to interpret

1. **`body_width` = 3.90 nom, status `inferred`.** The only dimension in the
   gold. The quote is the ordering code on page 39, `SN = Plastic SOIC
   (3.90 mm body), 8-lead`. The datasheet states the body size in text there
   and in the package-marking heading on page 14 (`8-Lead SOIC (3.90 mm)`), but
   never as a dimensioned table row (page 18 is unreadable). Which axis 3.90 is
   had to be interpreted: the page-17 outline shows `E1` (across the lead rows,
   i.e. across the two rows of leads) measuring the 3.90 side, and the KiCad
   footprint name `3.9x4.9mm` agrees. `inferred` because of that derivation.
2. **`SDA` typed `bidirectional`, status `extracted`.** Chosen over
   `open_collector` because the datasheet calls the pin bidirectional (§2.2)
   and only describes the driver as open drain; the skill's open-drain rule is
   about outputs.
3. **`A0`/`A1`/`A2`/`SCL` typed `input`, status `extracted`.** Table 2-1 has no
   I/O column, so the direction comes from §2.1 ("the A0, A1 and A2 inputs")
   and §2.3 ("This input"), both on page 5. The `source.quote` carries the
   table row (name and pin numbers); the type evidence is in the surrounding
   prose on the same page.
4. **`VSS`/`VCC` typed `power_in`, status `inferred`.** Table 2-1 says "Ground"
   and "+2.5V to 5.5V (24LC256)"; the supply/ground rule makes both
   `power_in`, and the skill marks that choice `inferred`.
5. **No `group` on any pin.** The datasheet shows one device with no repeated
   functional blocks. Nine of the eleven existing gold cases leave the supply
   pins ungrouped; only `lm358_soic8` uses `power`, and that part has units.
6. **No `alt_names`.** "User Configurable Chip Select" (A0–A2) and "Serial
   Data"/"Serial Clock" are descriptions, not alternate functions of a
   multi-function pin.
7. **Package family `SOIC`.** The datasheet calls it "8-Lead Plastic Small
   Outline (SN) – Narrow, 3.90 mm Body [SOIC]" (page 17).

## Where the datasheet contradicts itself

1. **`D` is labelled "Overall Length" in the SOIC table but is the moulded
   length.** Page 18 lists `Overall Length D 4.90 BSC` and gives no moulded
   length, yet on the page-17 top view the `D` extension lines drop to the two
   *moulded* body ends and the lead row (4 leads at 1.27 pitch = 3.81 mm
   centre-to-centre) lies entirely inside that span. The same datasheet's
   TSSOP table (page 23) labels the same letter `Molded Package Length D`
   (2.90/3.00/3.10). So `D` on page 18 is the body length; the label is
   JEDEC's, where `D` also means "overall length" for SOIC. Whoever adds the
   dimension should use `body_length`, not `overall_length`, because the SOIC
   leads do not project past the body ends — the tip-to-tip extent along the
   rows is the body's 4.90 either way, and KiCad's footprint confirms a 4.9 mm
   body. This does not affect the gold, which leaves the dimension out.
2. **The page-5 note about an exposed pad that is not in the table.** "Note:
   Exposed pad on DFN/TDFN can be connected to VSS or left floating." Table 2-1
   gives both DFN and TDFN exactly eight numbered pins and no exposed pad.
   Irrelevant to SOIC-8, but it would matter to a DFN gold for this part.
3. **The MSOP row `(NC) — — — — 1, 2 — — —`** is placed between A1 and A2 in
   the table, so the MSOP column is not in pin order. Harmless for SOIC, which
   has no NC pin — this is why the gold has no `no_connect` pin despite the
   table having a "Not Connected" row.

## What is in the gold

- 8 pins, all `extracted` except the two supply pins.
- 1 dimension, `body_width` 3.90 nom.
- No footprint is generated: `kicad-partspec build` reports `footprint.skipped`
  and asks for `pitch`, `land_pad_length`, `land_pad_width`, `land_span` and
  `body_length`, all of which are readable on pages 18 and 19 but none of
  which can be cited from this PDF's text layer.