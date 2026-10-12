# MCP23008 (SOIC-18) gold review

Datasheet: `mcp23008.pdf`, sha256 `3516fba5df6da78c2e7a58defaf90e4bdb9fb71f904e56b74b502fab0b4d112c`,
DS20001919F (Revision F, March 2019). PDF page numbers equal the printed page numbers throughout
(checked on pages 1-4, 33, 34, 40).

Parts used: **SOIC, 18-lead wide body (7.50 mm)**, drawing `C04-051D` (pages 32-33) and land
pattern `C04-2051A` (page 34). The PDIP, SSOP and QFN drawings in Section 3.0 were ignored.

Cross-check references:
- Symbol: `MCP23008-xSO` in `/usr/share/kicad/symbols/Interface_Expansion.kicad_sym` (no `extends`;
  pins live in `MCP23008-xSO_1_1`).
- Footprint: `/usr/share/kicad/footprints/Package_SO.pretty/SOIC-18W_7.5x11.6mm_P1.27mm.kicad_mod`.

## 1. Disagreements with KiCad

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| 1 | `land_span` | 9.40 mm centre-to-centre ("Contact Pad Spacing", dimension `C`, NOM column) | pad centres at x = ±4.65 → span 9.30 mm | **Datasheet: 9.40.** KiCad's pad geometry is IPC-7351-derived, not the vendor land pattern. | 34 |
| 2 | `land_pad_length` / `land_pad_width` | 1.90 × 0.60 mm (Contact Pad Length `Y` / Width `X`) | 2.05 × 0.60 mm | **Datasheet.** The task statement notes KiCad pad *size* may legitimately differ (IPC-7351). `land_pad_width` (0.60) agrees. | 34 |
| 3 | `body_length` | `D` = 11.55 BSC, labelled "Overall Length" | footprint name says 11.6 mm; `F.Fab` outline is 8.00 × 11.26 mm | **Datasheet: 11.55**, recorded as `body_length`. Agree within IPC/fab allowance. | 33 |
| 4 | Pin 3 `A2` type | Pin Type column prints `I/O` (page 4), but the MCP23008 pinout figure (page 2) draws a single-headed arrow into pin 3 and the Function cell reads "Hardware address input (**MCP23008**)" | `input` | **`input`.** Two MCP23008-specific places on the datasheet say input; the shared `I/O` is the union with MCP23S08 pin 3 = `SO` (output). See §3. | 2, 4 |
| 5 | Pin 7 `NC` type | Pin Type column prints `I` (page 4); Function cell reads "No connect (**MCP23008**)", and the page-2 figure draws a bare line with no arrow | `no_connect` | **`no_connect`.** Agrees with KiCad; the `I` in the type column belongs to MCP23S08 pin 7 = `CS` (input). See §3. | 2, 4 |
| 6 | Pin 6 `RESET` polarity | Printed as RESET with an overbar (p.4 table, and `RESET̅` on the p.2 pinout figure) | `~{RESET}` | **Datasheet: `RESET-`.** The gold records the trailing ASCII hyphen, the carrier for the printed overbar per `reference.md`'s convention ("the primary function as printed. Use the ASCII hyphen (`IN1-`, `V-`)"), which also matches KiCad's `~{RESET}`. | 2, 4 |
| 7 | Alt functions of pins 1, 2, 3, 7 | Page-4 Pin Name cells read `SCL/SCK`, `SDA/SI`, `A2/SO`, `NC/CS` | no alt names | Gold records **no `alt_names`**. The second half of each cell is the MCP23S08 (SPI) function of the same pad; this part is the I²C MCP23008, whose page-2 figure prints only `SCL`, `SDA`, `A2`, `NC`. Per the skill's figure-over-table rule the figure name is primary and no alt is recorded. Agrees with KiCad. | 2, 4 |

Items that **agreed** with KiCad and needed no decision: pin count 18; every pin number; names
`SCL SDA A2 A1 A0 RESET- NC INT VSS GP0…GP7 VDD` (note the ground pin is printed `VSS` in the text
layer of both page 2 and page 4 — the page image renders it in small caps as `Vss`, but the
underlying characters are `VSS`, so KiCad's `VSS` is correct); `GP0…GP7` and `SDA` bidirectional;
`SCL A1 A0 RESET-` input; `INT` output; `VSS`/`VDD` `power_in`; pitch 1.27 mm.

## 2. Values that had to be interpreted

- **`body_length` ← "Overall Length `D` = 11.55 BSC"** (page 33). `D` is printed as an overall
  length, but for this SOIC the leads do not project past the body ends, and note 3 says `D` excludes
  mold flash, protrusions and gate burrs — i.e. `D` *is* the moulded body length along the pin rows.
  Recorded as `body_length`, status `inferred`. No `overall_length` is recorded: the drawing gives no
  separate tip-to-tip dimension along the rows.
- **`overall_width` ← "Overall Width `E` = 10.30 BSC"** (page 33). Directly the skill's dual-row
  definition (lead tip to lead tip, across the rows, largest across-rows dimension on the outline).
  Cross-check: `E` (10.30) > `E1` (7.50) as tip-to-tip must be.
- **`land_span` ← "Contact Pad Spacing `C` = 9.40"** (page 34). The land-pattern figure shows `C`
  running from the dashed centre line through the top pad row to the dashed centre line through the
  bottom pad row, i.e. centre-to-centre between rows. Status `inferred`.
- **`land_pad_width` / `land_pad_length` recorded as `nom`, not `max`.** Both are printed in the MAX
  column of the land table, but land-pattern values are reference values rather than limits
  (evals README "Conventions"; same treatment as the CP2102N gold, whose land table also prints one
  value across Min/Max).
- **`L1` = 1.40 REF ("Footprint") left out.** It is the body-to-tip lead length; the skill explicitly
  excludes that from `lead_length`, and no name in the dimension list covers it. `lead_length` is
  `L` = "Foot Length" 0.40-1.27 (the flat part resting on the board), confirmed in Detail A on page 33.
- **Left out because no name fits:** `N` = 18 (it is the pin count, already in `package.pin_count`),
  `h` chamfer 0.25-0.75, lead angle 0°, foot angle 0-8°, mold draft angles top/bottom 5-15°.
- **Pin names taken from the MCP23008 figure (page 2)**, which agrees pin-for-pin with the SOIC column
  of TABLE 1-1 (page 4). Page 3 is the MCP23S08 figure and was not used.
- **Pin 3 and pin 7 types** come from the page-2 figure arrows and the page-4 Function cells, not from
  the Pin Type column (see §1 rows 4 and 5).
- **No `group` on any pin.** `GP0…GP7` are one 8-bit port, not repeated identical functional units; the
  supply pins are not marked `"power"` (matching the round-2 golds, which use no groups at all).
- **`RESET-` overbar** carried as the trailing ASCII hyphen in the name, per `reference.md`'s
  `IN1-` / `V-` convention (row 6 above).
- **`VSS`** taken from the text layer, not from the small-caps rendering on the page image (see §1).

## 3. Places where the datasheet contradicts itself

1. **Pin Type column is a union across MCP23008 and MCP23S08.** Pin 3 is typed `I/O` although the
   MCP23008 figure and the Function cell both call it an input, and pin 7 is typed `I` although the
   Function cell calls it a no-connect for the MCP23008. Resolved per pin in §1.
2. **Page 34 land table has a stray row.** "Contact Pad Spacing" appears twice: once as `C` = 9.40 and
   once more with no dimension letter and no value in any column. The valued row is used; the empty one
   is an editing leftover.
3. **The three package figures carry different pin maps.** Page 2 is the MCP23008 (I²C), page 3 is the
   MCP23S08 (SPI); the SOIC pins 1-8 read `SCL SDA A2 A1 A0 RESET NC INT` on page 2 but
   `SCK SI SO A1 A0 RESET CS INT` on page 3, for the same 18-pin package. Not a contradiction — two
   devices share one datasheet — but it makes the page-3 text extraction look like it contradicts
   TABLE 1-1 if you search for the SOIC column without reading the figure.
4. **Page 2 label casing.** The ground pin is rendered `Vss` in the page image but its text-layer
   characters are `VSS`. Not a contradiction, but the image alone would suggest the wrong name.