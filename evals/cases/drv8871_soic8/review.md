# DRV8871 (DDA, 8-pin SO PowerPAD) — gold PartSpec review

Datasheet: `drv8871.pdf`, SHA-256 `09de551a…1b548bf`, `SLVSCY9B – AUGUST 2015 – REVISED JULY 2016` (Rev. B), 27 pages.
Package outline: `DDA0008B` (page 24). Example land pattern: `DDA0008B` (page 25). Pin configuration and pin functions: page 3.

Sources used for the cross-check:

- KiCad symbol `DRV8871DDA`, `/usr/share/kicad/symbols/Driver_Motor.kicad_sym` (a leaf symbol; all pins are in
  `DRV8871DDA_1_1`, there is no parent symbol).
- KiCad footprints `Package_SO.pretty/SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm_ThermalVias.kicad_mod` (the generic
  IPC-7351 part) and `Package_SO.pretty/SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.95x4.9mm_Mask2.71x3.4mm_ThermalVias.kicad_mod`
  (the TI-specific part, which is what the DRV8871DDA symbol's `Footprint` property points at, under the name
  `Package_SO:Texas_HTSOP-8-1EP_…`). Both were read; the symbol names the Texas_HTSOP variant, and the generic
  EP2.29x3mm file is the one named in the task, so it is the primary comparison below.

## 1. KiCad disagreements

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| 1 | Pin 4 type | Pin Functions table, TYPE column `I` for `ILIM` (4) | `ILIM` is `passive` | **Datasheet wins: `input`.** The table prints a direction for this pin and the pin configuration figure agrees it is a control input (a resistor to ground sets the threshold). `passive` is KiCad's "no direction" fallback, not a statement about the pin. | 3 |
| 2 | Pin 7 name | Name column `PGND`, no. 7 ("High-current ground path"), TYPE cell `PWR` | A hidden pin named `GND`, number 7, `passive`, with no group | **Datasheet wins: name `PGND`, type `power_in`, group `power`.** KiCad merges the power ground into the logic ground and hides it; that is a symbol-layout choice, not the datasheet's name, type or grouping. The table prints `PWR` for this pin, and `reference.md` names the supply pins `"power"` among the permitted `group` values. | 3 |
| 3 | Pin 9 (exposed pad) name | Name column `PAD`, no. `—`, description "Thermal pad … Connect to board ground" | A hidden pin named `GND`, number 9, `passive`, with no group | **Datasheet wins: name `PAD`, group `power`.** The datasheet prints `PAD` in the NAME column and gives the pad no number, so the number 9 is `inferred`. The pad sits in the same supply/ground block as pins 1, 5 and 7 (see interpretation 11), so it carries `group: "power"` like them even though its TYPE cell is empty. | 3 |
| 4 | Pin 9 (exposed pad) type | TYPE column `—`; description says "Connect to board ground" | `passive` | **Datasheet wins: `power_in`, status `inferred`.** The TYPE cell is empty, but the description ties the pad to board ground, and `reference.md` maps an exposed pad tied to ground to `power_in`. The `passive` row ("no signal direction at all") is the weaker reading here. KiCad's own `passive` is a symbol-library convention for merged/hidden ground pins. | 3 |
| 5 | Package family / name | Outline drawing title: "PowerPAD™ SOIC - 1.7 mm max height / PLASTIC SMALL OUTLINE"; orderable addendum: "SO PowerPAD (DDA) \| 8" | Symbol description "HTSOP-8"; footprint name `Texas_HTSOP-8-1EP_…` | **Datasheet wins: `family: "SOIC"`.** The datasheet names the package SOIC in the drawing that defines every dimension, and "SO PowerPAD" in the addendum; `HSOP` is the older TI spelling that still appears on page 1 and page 3. See "Interpretations" below. | 24, 19, 1, 3 |
| 6 | Exposed-pad land size | Land pattern metal pad `(2.95)` × `(4.9)`, both NOTE 9 | Generic `EP2.29x3mm`; TI-specific `EP2.95x4.9mm` | **Datasheet wins.** The TI-specific footprint reproduces `(2.95) × (4.9)` exactly, which confirms the reading of the drawing. The generic EP2.29x3mm is IPC-7351-derived (roughly the mid-point of the package EP 2.11–2.71 × 2.8–3.4) and does not follow this land pattern. Our generator can only emit a square EP pad; see "Interpretations". | 25 |
| 7 | Land pad size / row spacing | Land pattern: `8X (1.55)` × `8X (0.6)` pads, row centres `(5.4)` apart, pitch `6X (1.27)` | Pads 1.95 × 0.6 at x = ±2.475 (generic) / 1.775 × 0.6 at x = ±2.5625 (TI-specific) | **Datasheet wins.** KiCad's pad sizes and row spacing come from IPC-7351 density levels, not from this drawing, which is the documented legitimate difference. Pad *width* (0.6), *pitch* (1.27) and *body* agree exactly. | 25 |
| 8 | Body size | Outline: body 3.8–4.0 × 4.8–5.0 mm; overall width 5.8–6.2 mm | Footprint name says `3.9x4.9mm` | **Agreement.** 3.9 and 4.9 are exactly the mid-points of our `body_width` and `body_length` ranges. | 24 |
| 9 | Solder-mask opening on the exposed pad | `(2.71)` × `(3.4)`, labelled "SOLDER MASK OPENING" / "SOLDER MASK DEFINED PAD" | Symbol footprint property says `Mask2.4x3.1mm` | **Datasheet wins: `(2.71) × (3.4)`.** Not recorded in the PartSpec (no `land_*` name for a mask opening); the TI-specific KiCad footprint's name agrees with the datasheet here (`Mask2.71x3.4mm`), and the symbol property's 2.4x3.1 is a rounded restatement. | 25 |

Pins 1 (`GND`), 2 (`IN2`), 3 (`IN1`), 5 (`VM`), 6 (`OUT1`), 8 (`OUT2`) agree with the KiCad symbol on number, name and
electrical type. The footprint pad count (9 pads, 1–8 plus the EP), pitch, row count and body size also agree.

KiCad's symbol records no `group` on any pin, including the hidden ground pins it shows at 7 and 9, so on grouping
**the datasheet wins**: this gold records `group: "power"` on pins 1 (`GND`), 5 (`VM`), 7 (`PGND`) and 9 (`PAD`).
The TYPE column of the page-3 Pin Functions table prints `PWR` for the first three — "GND 1 PWR Logic ground",
"VM 5 PWR supply", "PGND 7 PWR High-current ground path" — and pin 9's own row, "PAD — — Thermal pad", carries the
description "Connect to board ground", tying it to the same supply/ground block. `reference.md` lists the supply pins
`"power"` among the permitted `group` values. Grouping a symbol's hidden power pin away from the visible signal pins is
a symbol-layout convenience; the datasheet's block is the statement of intent. This gold was previously the odd one out
among the supply-pin cases: `tlc555_soic8` and `lm358_soic8` already group their supply pins `power`.

## 2. Values that had to be interpreted

1. **`package.family` = `SOIC`.** The datasheet uses three names for this package: "8-Pin HSOP With PowerPAD™" and
   "HSOP (8)" (pages 1 and 3), "SO PowerPAD (DDA) | 8" (orderable addendum, page 19), and "PowerPAD™ SOIC - 1.7 mm max
   height / PLASTIC SMALL OUTLINE" on the package outline and land pattern drawings (pages 24 and 25). `SOIC` was
   chosen because it is the name on the drawing that defines every dimension, and because the other two spellings mean
   the same JEDEC MS-012 package (the drawing's own note 5 says "Reference JEDEC registration MS-012"). Note that
   this is *not* a rename to make the build succeed: `HSOP` is an unsupported family and would have produced a
   `footprint.skipped` warning.
2. **`overall_width` 5.8–6.2 (the `6.2 TYP / 5.8` pair).** Recorded as `min`/`max` because it is a stacked pair on the
   outline; the `TYP` is attached to the upper value and no separate `nom` was added (this matches the `lm358_soic8`
   gold, which records `[5.80-6.19]` the same way). This is the lead-tip-to-lead-tip dimension across the rows, the
   largest across-rows dimension on the outline. The `2X 3.81` lead centreline span next to it was deliberately **not**
   recorded: `reference.md` says a lead centre-to-centre span is not recorded.
3. **`lead_thickness` 0.10–0.25.** In the front view (page 24) a pair of arrows measures the vertical distance between
   two extension lines drawn off the top and bottom surfaces of the lead's toe, at the far end of the lead — clearly
   the lead's own thickness, not a standoff (the standoff is dimensioned separately in DETAIL A). The upper value
   carries `TYP`; like `overall_width` it is recorded as `min`/`max` with no `nom`. Marked `extracted`: the surfaces
   being measured are unambiguous on the rendered page. The page prints `0.25` twice (once for this pair, once in the
   `0.25 (M) C A B` gage-plane datum frame), so the quote deliberately includes `TYP 0.10`.
4. **`standoff` 0.00–0.15, marked `inferred`.** In DETAIL A (page 24) the upper arrow of the `0.15 / 0.00` pair points
   at a dashed horizontal line and the lower arrow at the lead's bottom face. The dashed line is the body underside
   extended out of the drawing; the solid line below it is the seating plane, which matches the `SEATING PLANE` datum
   label in the side view on the same page. That reading is what makes it a standoff, so it is `inferred` rather than
   `extracted`. This is the value `reference.md` warns is often ambiguous on SOIC drawings (`lm358_soic8` omits it
   entirely); here the drawing is unambiguous.
5. **`lead_length` 0.40–1.27.** The `1.27 / 0.40` pair in DETAIL A spans horizontally from where the lead leaves the
   body to the toe — the foot, so it is `lead_length` (and not the Nexperia-style "body to tip" `L`). It agrees with
   the `lm358_soic8` drawing `[0.41-1.27]`. The text layer interleaves this pair with the standoff pair
   (`0.15 0 -8 1.27 0.00 1 8 0.40`), so both quotes overlap; the binding was resolved on the rendered page.
6. **`ep_size` = 2.11–2.71, marked `inferred`.** The exposed thermal pad on the outline is **not square**: 2.11–2.71
   across the rows and 2.8–3.4 along them. `ep_size` is defined in `reference.md` as "side length … (square pads)" and
   the model holds a single value, so only the across-row pair is recorded. The along-row pair (2.8–3.4) is stated
   here and not in the spec.
7. **`land_ep_size` = 2.95, marked `inferred`.** The land pattern's exposed pad is also **not square**. The metal pad
   is `(2.95) × (4.9)` (both NOTE 9, "Size of metal pad may vary due to creepage requirement"); the solder-mask
   opening drawn inside it is `(2.71) × (3.4)`, labelled "SOLDER MASK DEFINED PAD" / "SOLDER MASK OPENING" /
   "METAL COVERED BY SOLDER MASK" — i.e. the mask opening is *smaller* than the copper, so the mask defines the pad.
   The generator builds a single square `land_ep_size` pad, so the across-row value `(2.95)` was taken (the direction
   that matches `body_width` and that KiCad's own `Texas_HTSOP-8-1EP_…EP2.95x4.9mm…` footprint also leads with).
   `land_*` values in parentheses are reference values, which `reference.md` allows. A generated footprint therefore
   has a 2.95 × 2.95 mm EP where the datasheet's copper is 2.95 × 4.9 mm: **the exposed pad is too short along the
   pin rows, and the pad is not a perfect fit for this package.** This is the one place where the PartSpec format
   cannot express the datasheet.
8. **`land_span` = 5.4, marked `inferred`.** A bare parenthesised number; the endpoints were read off the rendered
   land pattern (the dimension arrows run between the two pad centre lines, and the adjacent `(1.3) TYP` half-span
   confirms the centre lines). Marked `inferred` for the same reason as the `lm358_soic8` gold's `land_span`.
9. **Pin 9 number = `9`, marked `inferred`.** The datasheet prints `—` in the NO. column and calls the pad "Thermal
   Pad" in the pin configuration figure. `9` is `pin_count + 1` per `reference.md`.
10. **Pin 2 (`IN2`) quote comes from the pin configuration figure**, not the table. In the Pin Functions table the TYPE
    cell is vertically centred across the `IN1`/`IN2` pair, so the text layer puts no `I` next to either row on its
    own. The rendered page shows the `I` cell spanning both rows; the quote `"IN2 2 7 PGND"` is the figure, where the
    name and number sit side by side, so the pairing is proven by the quote itself.
11. **`group` = `"power"` on pins 1 (`GND`), 5 (`VM`), 7 (`PGND`) and 9 (`PAD`).** `reference.md` names the supply pins
    `"power"` among the permitted `group` values ("only when the datasheet shows repeated, identical functional blocks —
    two identical amplifiers, a quad gate: `"A"`, `"B"`, and the supply pins `"power"`"). The page-3 Pin Functions table
    prints the TYPE cell `PWR` for the first three, quoting the block directly: "GND 1 PWR Logic ground",
    "VM 5 PWR supply", "PGND 7 PWR High-current ground path" — a four-row supply/ground block including the exposed
    pad, whose row is "PAD — — Thermal pad" with the description "Thermal pad … Connect to board ground". Pin 9 has no
    printed TYPE cell, so it is the softest of the four, but nothing in `reference.md` excludes it and its description
    puts it in the same supply/ground block as pins 1, 5 and 7. An earlier draft of this gold omitted `group` on all
    four with no datasheet reason; the adjudicator ruled that a **run was right and the gold was wrong**. The gold now
    groups all four, which also makes it consistent with `tlc555_soic8` and `lm358_soic8`, whose supply pins are
    already grouped `power`. No `A`/`B` units exist: the DRV8871 is one H-bridge with one set of control inputs, so
    the two bridge outputs and the two logic inputs are not repeated units and stay ungrouped.
12. **Not recorded, deliberately:** `2X 3.81` (lead centre-to-centre span, excluded by `reference.md`), `4X (0°–10°)`
    and `0°–8°` (lead angles), `0.25 (M) C A B` and `0.1 C` (datum / gage-plane callouts, not package dimensions),
    `0.07 MAX/MIN ALL AROUND` (solder-mask expansion), `(1.3) TYP` (the two callouts on the land pattern that sit on the
    symmetry axis and on the pad/via centre lines: they give the 1.3 mm thermal-via grid pitch, which the pad pitch
    already covers), `(R0.05) TYP` and `(0.2) TYP` (via radius and diameter), `body_thickness` (the outline gives only the overall 1.7 mm height, not the body alone).

## 3. Where the datasheet contradicts itself

1. **"Body size".** Page 1 (Features and the Device Information table) calls the package
   "4.9 × 6 mm" and "BODY SIZE (NOM) 4.90 mm × 6.00 mm". The package outline on page 24 gives a plastic body of
   **3.8–4.0 mm × 4.8–5.0 mm**, with **5.8–6.2 mm** across the lead rows. So the advertised "6.00 mm" is the
   overall lead-tip-to-lead-tip width, not a body dimension, and the advertised "4.90 mm" is the body length. The gold
   follows the drawing. (This is also why KiCad names the footprint `3.9x4.9mm`.)
2. **Package name.** "HSOP (8)" / "8-Pin HSOP With PowerPAD™" (pages 1, 3) versus "PowerPAD™ SOIC" (pages 24, 25) and
   "SO PowerPAD (DDA) | 8" (page 19) for the same DDA package. See interpretation 1.
3. **Drawing revision is newer than the datasheet revision.** The document is Rev. B, "REVISED JULY 2016", but every
   mechanical drawing is stamped `4214849/B 09/2025`, and the PDF was produced in November 2025. The outline and
   land pattern have therefore been re-issued (or the datasheet re-hosted) without a document-revision bump, so the
   dimensions above come from a 2025 drawing inside a 2016 document.
4. **`DRV8871DDA` (the 8-pin, non-tape-and-reel orderable part this gold describes) is marked "Obsolete"** in the
   orderable addendum on page 19, while `DRV8871DDAR` and friends are Active. That does not affect the pinout or the
   package, but a reader following the addendum would not order this part number.
5. **Thermal-pad mask scheme.** The land pattern labels the exposed pad "SOLDER MASK DEFINED PAD" while the solder-mask
   details below are headed "PADS 1-8" with both "NON SOLDER MASK DEFINED" and "SOLDER MASK DEFINED" variants shown.
   Not strictly contradictory, but it means the `(2.95) × (4.9)` copper and the `(2.71) × (3.4)` opening are two
   different rectangles on the same page, which is easy to misread.

## 4. Build result

`kicad-partspec validate` passes with 0 failures and 8 `status.inferred` warnings (pins 1, 5, 7, 9; dimensions
`standoff`, `ep_size`, `land_span`, `land_ep_size`). Every `source.quote` was re-checked against the cited page of
this PDF with `check_gold`'s quote check (whitespace-collapsed `pdftotext -layout`): 0 quotes missing.

`kicad-partspec build` produces `DRV8871.kicad_sym` and
`partspec.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod` (9 pads: 1–8 roundrect at x = ±2.7, pitch 1.27, 1.55 × 0.6 mm,
plus a 2.95 × 2.95 mm rectangular EP at the origin). `kicad-partspec verify` on the two generated files passes.