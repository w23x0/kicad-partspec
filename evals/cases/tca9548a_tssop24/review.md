# TCA9548APWR (PW, TSSOP-24) — gold review

Datasheet: `tca9548a.pdf`, SHA-256 `2137822f…0a2dc`, `SCPS207H – MAY 2012 – REVISED SEPTEMBER 2024` (Rev. H, September 2024).

Package chosen: **PW (TSSOP), 24 pins, no exposed pad** — this is the package of the MPN `TCA9548APWR`
listed in the orderable addendum (p. 27) and the package of the KiCad cross-check
(`Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm`). The datasheet covers three packages (PW / RGE VQFN / DGS VSSOP);
everything below is taken from the PW drawings only: pin table + Figure 4-1 (p. 3), PW0024A outline (p. 36),
PW0024A land pattern (p. 37).

Every pin was read from Table 4-1 (p. 3) and the number↔name pairing was checked against Figure 4-1
(top view of PW/DGS) on the rendered page 3. They agree for all 24 pins.
Every dimension was read from the rendered page 36 / 37.

## 1. Disagreements with the official KiCad library

### Symbol — `/usr/share/kicad/symbols/Interface_Expansion.kicad_sym`, `TCA9548APWR` (24 pins, no `extends`)

| # | Pin | Datasheet (page) | KiCad | Decision |
|---|---|---|---|---|
| 1 | 5, 7, 9, 11, 14, 16, 18, 20 (`SC0`–`SC7`) | Type column `I/O` (p. 3, Table 4-1) | `output` | **Datasheet wins: `bidirectional`.** The type column of Table 4-1 prints `I/O` for every serial pin; the skill's rule maps `I/O` to `bidirectional`. KiCad's `output` is its own reading of "the switch drives the clock downstream". The part cannot drive a clock into an idle channel without a pull-up, and the datasheet prints no separate direction for these pins. |
| 2 | 22 (`SCL`) | `I/O` (p. 3) | `input` | **Datasheet wins: `bidirectional`.** Same reasoning; the pin carries the controller's clock and is listed with the other bus pins. |
| 3 | 3 | Name printed `RESET`; description "Active-low reset input" (p. 3) | `~{RESET}` | **Datasheet wins: name `RESET`.** Active-low is polarity, printed in the description, not in the name; the table and both pinout figures print plain `RESET`. |

Everything else agrees with KiCad: 24 pin numbers, all 24 names (`A0`/`A1`/`A2` inputs, `SD0`–`SD7` and
`SDA` bidirectional, `SC0`–`SC7` names, `SCL`, `RESET`), `GND`/`VCC` as `power_in`.
Those three rows above are the only symbol differences; they change the generated symbol's pin types for
9 pins and one pin name.

### Footprint — `Package_SO.pretty/TSSOP-24_4.4x7.8mm_P0.65mm.kicad_mod`

| Quantity | Datasheet | KiCad | Decision |
|---|---|---|---|
| Pad count | 24 (p. 37) | 24 | agree |
| Pitch | 0.65 (p. 36 `22X 0.65`) | 0.65 (pad y = ±3.575 … ±0.325) | agree |
| Pin-1 position / pad numbering | pin 1 top-left, counter-clockwise, 1–12 left, 13–24 right (Figure 4-1, p. 3; land pattern p. 37) | same (pad 1 at x=−2.8625, y=−3.575) | agree |
| Body | 7.7–7.9 × 4.3–4.5 (p. 36) | fab outline 4.62 × 8.07, name says 4.4x7.8 | agree (KiCad's fab outline adds its usual margin) |
| Pad size | land pattern 1.5 × 0.45 (p. 37) | 1.475 × 0.4 | **Not a disagreement**: KiCad pads come from IPC-7351 nominal, the datasheet numbers are the recommended land pattern. The generated footprint uses the datasheet's 1.5 × 0.45. |
| Row spacing | `land_span` 5.8 (p. 37) | 5.725 (pad x = ±2.8625) | Same kind of difference as the pad size: IPC-7351 nominal vs the datasheet's recommended land. The build uses the datasheet's 5.8; KiCad keeps 5.725. |

No dimension in the gold was taken from KiCad, and no KiCad value was adopted.

## 2. Values that had to be interpreted

| Value | Why it needed a decision | How it was decided |
|---|---|---|
| `overall_width` = 6.2 / 6.6 (p. 36) | The dimension is drawn across the lead rows, but both values carry `TYP`, which reads like two typicals rather than a limit pair. | Rendered at 600 dpi: the extension lines sit on the **lead tips**, not on the body edges, and the body edges carry dimension B (4.3/4.5). Recorded as min 6.2 / max 6.6, same treatment as the identical callout on the PW0020A drawing in `txs0108e_tssop20`. |
| `body_length` = 7.7 / 7.9 vs `body_width` = 4.3 / 4.5 | The outline is drawn rotated (pins 1–12 run down the left side), so it is not obvious which axis is "length". | Rendered page 36: the 7.7/7.9 dimension is parallel to the pin rows (the 12-pitch direction, 2×7.15), 4.3/4.5 is across them. `body_length` = along the rows, `body_width` = across, per the skill's dual-row rule. Checked against the standard TSSOP-24 7.8 × 4.4 body. |
| `lead_width` = 0.19 / 0.30 (p. 36, `24X 0.30 / 0.19`) | In the top view the leads run horizontally; the arrow pair could be read as the lead length. | Rendered at 600 dpi: the arrows span the lead's vertical extent in the top view, and the callout carries the position-tolerance frame `⌖ 0.1(M) C A B` for the 24 leads — i.e. it sizes the lead across. Recorded as `lead_width`. |
| `lead_length` = 0.50 / 0.75 (p. 36, Detail A) | Detail A also carries `0.15/0.05`, so the two must not be confused. | Rendered at 600 dpi: 0.50/0.75 runs horizontally from the toe to the point where the lead turns up into the body — the foot resting on the board. Recorded as `lead_length`. |
| `standoff` = 0.05 / 0.15 (p. 36, Detail A) | The front view prints `(0.15) TYP` on what looks like the same feature, and Detail A's `0.15 / 0.05` reads like a lead gauge pair. | Recorded Detail A's limit pair as the **standoff**: its extension lines run from the gage/seating plane to the body underside, so it measures how far the part stands off the board, not the metal. The same callout is the standoff on DCU0008A (`0.1 / 0.0`) and on PW0016A. `(0.15) TYP` in the front view cannot be used instead: it is parenthesised, and Note 1 on the drawing makes a parenthesised value a **reference dimension**, not a package limit — so no `lead_thickness` entry remains. |
| `0.25` beside `GAGE PLANE` (p. 36) | Could be read as the standoff. | Left **out**. Rendered at 600 dpi: the leader points at the gage-plane line (the plane at which the lead is measured), not at the body underside, so `0.25` is not a standoff. The standoff is Detail A's `0.15 / 0.05`. |
| `⌒ 0.1 C` and `⌖ 0.1(M) C A B` (p. 36) | Numeric callouts on the outline. | Left **out**: profile-of-surface and true-position geometric tolerances, not linear dimensions. |
| `land_span` = 5.8, status `inferred` (p. 37) | The value is printed only as `(5.8)`; whether it is centre-to-centre or pad-edge to pad-edge has to be read off the drawing. | Rendered page 37: the two extension lines drop from the dash-dot centre lines of the pad columns, so it is centre-to-centre. Marked `inferred` because that reading is an interpretation. |
| `GND` (12) and `VCC` (24) as `power_in`, status `inferred` | The type column prints `—` for GND and `Power` for VCC; neither is a KiCad type. | Skill's supply/ground rule; status `inferred` as required. |
| `group` on 18 pins: `CH0`–`CH7` on `SD0`/`SC0` … `SD7`/`SC7` (16 pins), `power` on `GND` (12) and `VCC` (24) | Whether eight identical downstream channels count as "repeated identical functional blocks". | Recorded the groups. The channels are the datasheet's own units, not a reviewer's invention: p. 1 says "one sensor can be connected at each channel: 0-7", the p. 16 overview calls it an "8-channel, bidirectional translating I2C switch … directed to eight channels of target devices, SC0/SD0-SC7/SD7", and the p. 13 §7.2 functional block diagram draws eight identical switches. Table 4-1 (p. 3, which the pins cite) prints the channel number in each pin name. `reference.md` offers `"A"`/`"B"` only as examples of a key; `power` is the key it names for supply and ground pins. The two pins of one channel share one key, so the `SDn`/`SCn` pair stays together. `A0`, `A1`, `A2`, `RESET`, `SDA` and `SCL` are the part-level bus, address and control pins, not channel units, so they stay ungrouped. |
| `mpn` = `TCA9548APWR` | The datasheet's front page names the device TCA9548A and covers three packages. | Taken from the orderable addendum, p. 27, the TSSOP (PW) ordering code for the part under test, and matching the KiCad symbol name. |
| `exposed_pad` = false, `pin_count` = 24 | The VQFN sibling has a thermal pad (Figure 4-2). | PW has none: the thermal table on p. 5 prints `RθJC(bot) N/A` for PW (present for RGE), and PW0024A's outline shows no pad. |

## 3. Contradictions inside the datasheet

- **Table 4-1 prints two pin-number columns** (`TSSOP, VSSOP (PW, DGS)` and `VQFN (RGE)`) and they
  disagree for almost every pin — e.g. pin 1 is `A0` in the PW column and `SD0` in the RGE column;
  pin 3 is `RESET` (PW) vs pin 24 (RGE). This is not a contradiction, it is the same die in three packages,
  but it means a quote must be taken from the PW column, which is what the gold does. Figure 4-1
  (PW/DGS top view) agrees with the PW column on all 24 pins.
- **Figure 4-2 (RGE) shows a "Thermal Pad" with no pin number** and no row in Table 4-1. Irrelevant for
  PW, but a reader who takes pin numbers from Figure 4-2 gets the RGE numbering, not the PW one.
- **The `6.6 TYP / 6.2 TYP` callout** labels both ends of a limit pair `TYP`, which contradicts how `TYP`
  is used everywhere else on the drawing (e.g. `(0.15) TYP`, `2X 7.15` boxed as basic). Treated as a
  range; flagged above.
- Revision H added the DGS (VSSOP) package and changed terminology; nothing that affects this part.

## 4. Validation

- `kicad-partspec validate spec.gold.json --datasheet tca9548a.pdf` → **passed**, 0 failures,
  3 `status.inferred` warnings (pins 12 and 24, `land_span`), which are the honest ones.
- `kicad-partspec build spec.gold.json --out out --concise` → **passed**, 0 failures, 0 build warnings.
  A footprint **was** generated: `out/partspec.pretty/TSSOP-24_4.4x7.8mm_P0.65mm.kicad_mod` — the same
  name KiCad uses, 24 pads, pitch 0.65, body outline 4.4 × 7.8, pads 1.5 × 0.45 at ±2.9 (the datasheet's
  land pattern). `out/TCA9548APWR.kicad_sym` carries all 24 pins.

## Round-4 corrections

Two changes were made to this gold after it was first written; nothing else was touched.

### 1. `group` added to the channel and supply pins

- **Change:** pins 4/5, 6/7, 8/9, 10/11, 13/14, 15/16, 17/18, 19/20 (`SD0`/`SC0` … `SD7`/`SC7`) get
  `"group": "CH0"` … `"CH7"`; pins 12 (`GND`) and 24 (`VCC`) get `"group": "power"`. No pin's `status`
  changed and no new source quote was added — the pins already cite page 3, whose Table 4-1 prints the
  channel number inside each pin name (`SD0 4`, `SC7 20`, …).
- **Why:** the first version of this file recorded no `group` on any pin, reading eight channels as one
  function rather than eight units. That was wrong, and the extraction runs were right. The evidence is in
  the datasheet's own words: p. 1, "one sensor can be connected at each channel: 0-7"; p. 13 §7.2, the
  functional block diagram with eight identical switches; p. 16, "The TCA9548A is an 8-channel,
  bidirectional translating I2C switch … directed to eight channels of target devices, SC0/SD0-SC7/SD7.
  Any individual downstream channel can be selected as well as any combination of the eight channels".
- **Key names:** `CH0`–`CH7` follow the datasheet's channel numbers. `reference.md` gives `"A"`/`"B"` only
  as examples of a group key, and reserves `power` for supply and ground pins, so the two power pins take
  `power` alongside the channel groups rather than a channel-style key.

### 2. `lead_thickness` renamed to `standoff`

- **Change:** the dimension key `lead_thickness` becomes `standoff`; page 36, the quote `0.15 0.05`,
  `min` 0.05, `max` 0.15 and status `extracted` are unchanged. No `lead_thickness` entry remains.
- **Why:** Detail A's `0.15 / 0.05` runs from the gage/seating plane to the body underside, so it is the
  standoff — the same callout and the same reading as DCU0008A (`0.1 / 0.0`) and PW0016A. The sheet's only
  thickness callout is `(0.15) TYP` in the front view, and a parenthesised value is a **reference
  dimension** under Note 1 on the drawing, not a package limit; it therefore cannot stand in for a
  `lead_thickness` entry, and a limit pair was being recorded against a feature the drawing does not limit.
