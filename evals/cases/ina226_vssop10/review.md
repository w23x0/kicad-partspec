# INA226 (VSSOP-10, DGS0010A) — gold review

Datasheet: `ina226.pdf`, SHA-256 `c9b67f88…03ca2d`, revision **SBOS547C** (cover header
"SBOS547C – JUNE 2011 – REVISED AUGUST 2026"; §10 Revision History: "Changes from Revision B
(September 2024) to Revision C (August 2026)").

Pages used: **p.3** (§4 Pin Configuration and Functions: Figure 4-1 pinout + Table 4-1),
**p.38** (PACKAGE OUTLINE DGS0010A), **p.39** (EXAMPLE BOARD LAYOUT / land pattern).

Every pin and every dimension was read from `pdftotext -layout` and then confirmed on the
rendered page image at 150 dpi (and 400 dpi for Detail A / the lead-thickness callout).

## 1. KiCad cross-check — every disagreement

Sources: `Sensor_Energy.kicad_sym` symbol `INA226` (self-contained, no `extends`) and
`Package_SO.pretty/VSSOP-10_3x3mm_P0.5mm.kicad_mod`.

| # | Item | Datasheet (gold) | KiCad | Decision | Page |
|---|---|---|---|---|---|
| 1 | pin 8 name | `VBUS` (Table 4-1 and Figure 4-1) | `Vbus` | Gold keeps `VBUS`. KiCad only lower-cases the interior of the name; not a different function. | 3 |
| 2 | pin 10 name | `IN+` (Table 4-1 and Figure 4-1) | `Vin+` | Gold keeps `IN+`. KiCad expands the pin name to the shunt-terminal form `VIN+` used in the electrical tables; the *pin label* printed in the pin table and pinout figure is `IN+`. | 3 |
| 3 | pin 9 name | `IN–` (printed with an en dash; ASCII `IN-` in the name field) | `Vin-` | Gold keeps `IN-`. Same reason as #2. | 3 |
| 4 | pin 3 name | `Alert` | `~{Alert}` (inversion bar) | Gold keeps `Alert`. The bar is a graphic overlay on the same primary name, not an alternate function. | 3 |
| 5 | footprint file name | body 3.0 × 3.0 mm, 10 pads, P0.5 mm (datasheet) | `VSSOP-10_3x3mm_P0.5mm` | Gold builds `VSSOP-10_3.0x3.0mm_P0.5mm.kicad_mod`. Same footprint; only the name string differs, and the builder derives it from the datasheet body size. | 38/39 |

**No disagreement on electrical type.** All ten pins match KiCad exactly:

| Pin | Gold | KiCad |
|---|---|---|
| 1 A1 | input | input |
| 2 A0 | input | input |
| 3 Alert | open_collector | open_collector |
| 4 SDA | bidirectional | bidirectional |
| 5 SCL | input | input |
| 6 VS | power_in | power_in |
| 7 GND | power_in | power_in |
| 8 VBUS | input | input |
| 9 IN- | input | input |
| 10 IN+ | input | input |

**No disagreement on the footprint geometry.** The generated
`out/partspec.pretty/VSSOP-10_3.0x3.0mm_P0.5mm.kicad_mod` and KiCad's footprint agree on
10 SMD roundrect pads, pad size 1.45 × 0.30, pitch 0.5 (8 gaps), row centres at x = ±2.2
(span 4.4), 3.0 × 3.0 body. Note KiCad's `descr` field points at the ADS1115 datasheet; that
is only the URL of the footprint's provenance, not a geometry claim, and the ADS1115 is the
same JEDEC DGS package.

## 2. Values that had to be interpreted, and why

| Value | What had to be read | Why |
|---|---|---|
| `overall_width` 4.75–5.05 | The stacked `5.05 TYP` / `4.75 TYP` at the top of the top view. | The extension lines drop to the outer tips of pins 1/10 and 6/5, i.e. lead tip to lead tip **across** the two pin rows, which is `overall_width` by definition. Rendered at 400 dpi to confirm the extension lines attach to the lead tips, not to the body. Both numbers are marked `TYP`; recorded as `min`/`max` because they are a printed range. |
| `body_length` 2.9–3.1 | `3.1 / 2.9 NOTE 3`, datum A (left, vertical). | The pin rows in the top view are the two vertical columns, so the **vertical** body extent is along the rows → `body_length`. |
| `body_width` 2.9–3.1 | `3.1 / 2.9 NOTE 4`, datum B (bottom, horizontal). | Horizontal body extent, across between the rows → `body_width`. Both body dimensions print the same 2.9–3.1, so the assignment cannot be wrong by a number. |
| `lead_length` 0.4–0.7 (status `inferred`) | `0.7 / 0.4` in **Detail A**. | Detail A is drawn at a different scale from the top view, so its extension lines had to be traced. They run from the lead **toe** to the point where the lead leaves the board, stopping well short of the body face — i.e. the flat foot resting on the board, our `lead_length`, and *not* the "body to tip" length that `reference.md` says to leave out. Confirmed by measuring pixels on a 400 dpi render: the dimension's right extension line sits ~130 px left of the body edge. Cross-checks: 0.4–0.7 is JEDEC MO-187's VSSOP foot length, and (4.90 span − 3.00 body)/2 ≈ 0.95 mm per side leaves room for this foot plus the bend. The top view's own lead-length dimension is a boxed reference `2X [2]` with **no** value table anywhere in the datasheet, so it was left out. |
| `lead_thickness` 0.13–0.23 (status `inferred`) | `0.23 TYP / 0.13` in the side (front) view. | The arrows touch the top and bottom faces of the lead foot in the end-on view, so it is the material thickness, not a repeat of the `10X 0.27/0.17` lead **width** which is dimensioned in the top view. Marked `inferred` because the choice between the two views was a judgement call. |
| `standoff` 0.05–0.15 | `0.15 / 0.05` in Detail A. | The arrows span from the package underside down to the plane the lead foot rests on (the gage/seating plane), which is `standoff` by definition. |
| `land_pad_length` 1.45 | `10X (1.45)` on p.39. | In the land pattern the pads are horizontal rectangles and the leads point horizontally, so the 1.45 dimension (drawn across a pad, horizontally) is along the lead direction. |
| `land_pad_width` 0.3 | `10X (0.3)` on p.39. | The 0.3 dimension is the pad's vertical extent in the same drawing. Measured on the render (90 px ≈ 1.45 mm → 62 px/mm; pad height 21 px ≈ 0.34 mm) to confirm the two were not swapped. |
| `land_span` 4.4 (status `inferred`) | `(4.4)` on p.39. | The dimension line runs between the two row **centrelines**, so it is a centre-to-centre span, matching `land_span`'s definition. It carries no limit, only parentheses, so it is `nom`. |
| `family` = `VSSOP` | Cover page "10-pin DGS (VSSOP) package", Package Information table "DGS (VSSOP, 10)". | The datasheet's own name for the family; `pin_count` 10 matches the drawing's `8X` pitch callout (8 gaps between 10 leads). |

Things deliberately **left out**:

- `2X [2]` on the top view — a boxed reference dimension with no value table in the datasheet.
- `0.1 C` and `0.1 Ⓜ | C | A Ⓢ | B Ⓢ` — feature control frames (coplanarity/profile), not sizes.
- `0.25 GAGE PLANE`, `0° – 8°` (lead co-planarity angle) — Detail A tolerances, not one of our names.
- `(R0.05) TYP` (land pad corner radius) and the `0.05 MAX/MIN ALL AROUND` solder-mask
  expansion — no matching dimension name.
- No `alt_names` anywhere: Table 4-1 prints one function per pin. "Multi-functional alert" on
  pin 3 is a description of the alert, not a second printed function, so `Alert` gets no
  alternates. Likewise `VIN+`/`VIN–` in the Absolute Maximum Ratings are the same pins under
  their circuit symbol names, not alternate functions.
- No `group`: the part has one analogue front end and one I²C port — no repeated identical
  functional blocks and no amplifier/port units to name `A`/`B`. `IN+` and `IN-` are the two
  terminals of one shunt, which `reference.md` explicitly says stay ungrouped, and `VS`/`GND`
  are the only supply pair, so there is no repeated block to label `power`.

`IN-` is written with an ASCII hyphen in the `name` field as `reference.md` requires; the
`source.quote` keeps the en dash (U+2013) that the datasheet prints.

## 3. Places the datasheet contradicts itself

1. **Recommended Operating Conditions, p.4 (§5.3).** The table prints `VVS` operating supply
   voltage with **12 V** under MIN for common-mode input and **3.3 V** under NOM for supply
   voltage — i.e. the MIN/MAX cells are empty and the range the part actually has
   (2.7 V to 5.5 V) is missing. Verified on the rendered page: the cells really are blank,
   this is not a `pdftotext` artefact. It contradicts the Features bullet ("Operates from
   2.7V to 5.5V power supply"), the Description, and the pin-6 description
   ("Power supply, 2.7V to 5.5V"). Nothing mechanical depends on it.
2. **Common-mode range, p.4 vs p.1/p.4.** §5.3 gives a 12 V nominal common-mode input while
   the Features say the part "Senses bus voltages from 0V to 36V" and §5.1 gives a 40 V
   common-mode absolute maximum.
3. **Package size wording, p.1 vs p.38.** The Package Information table gives the package size
   as "3.00mm × 4.90mm" (length × width, *including pins*), which has to be read against the
   outline: the body is 3.0 × 3.0 mm and the 4.90 mm figure is the lead tip-to-tip span. Both
   are consistent once the footnote "(2) … includes pins" is applied, but the 3.00 × 4.90
   figure does not match either outline dimension on its own.
4. **Missing lead-length table.** The outline drawing calls out `2X [2]` for the lead length
   and Detail A gives the foot length, but the referenced dimension table is not present in
   the PDF at all, so the body-to-tip lead length cannot be extracted.

None of these touch the pin table or the mechanical values recorded in the gold.

## 4. Build result

`kicad-partspec validate spec.gold.json --datasheet ina226.pdf` → `passed: true`
(6 `status.inferred` warnings, 0 failures).
`kicad-partspec build spec.gold.json --out out --concise` → `passed: true`, 0 failures,
produced `out/INA226.kicad_sym` and
`out/partspec.pretty/VSSOP-10_3.0x3.0mm_P0.5mm.kicad_mod`.