# Review — TLC555 (SOIC-8, package D) gold PartSpec

Datasheet: `tlc555.pdf`, SHA-256 `1e4a94a0d87fb9a02d2b2030c3bd63113c1b020db8c4a23b4696f920a686b6d9`
(verified against `source.txt`), revision **SLFS043K — August 1983 — revised January 2026** (Rev. K).

Pages used, all found in `pdftotext -layout` and then confirmed on a 150 dpi render of the cited page:

| Page | Contents | Used for |
|---|---|---|
| 1 | Description + simplified schematic | cross-check of pin numbers only |
| 3 | Figure 4-1 (D/P/PS/JG 8-pin top view), Table 4-1 Pin Functions, Figure 4-2 (PW), Figure 4-3 (FK), Table 4-2 | all 8 pins |
| 13 | Figure 6-1 Simplified Schematic | cross-check of pin numbers only |
| 19 | PWM application figure | cross-check of pin numbers only |
| 30 | Package Option Addendum | orderable SOIC-8 part numbers |
| 38 | PACKAGE OUTLINE `D0008A`, drawing 4214825/C 02/2019 | 9 outline dimensions |
| 39 | EXAMPLE BOARD LAYOUT / LAND PATTERN EXAMPLE `D0008A`, same drawing number | 3 `land_*` dimensions |
| 40 | EXAMPLE STENCIL DESIGN `D0008A`, same drawing number | confirms the p.39 land values, nothing new |

Pin numbering was taken from Figure 4-1 and Table 4-1 (both on page 3) and independently
cross-checked against the simplified schematic on page 1, the Figure 6-1 simplified schematic on
page 13 and the PWM application figure on page 19. All agree:

`1 GND`, `2 TRIG`, `3 OUT`, `4 RESET`, `5 CONT`, `6 THRES`, `7 DISCH`, `8 VDD`

The datasheet also documents PW (TSSOP-14) and FK (LCCC-20) packages; neither is used here.
The D package has no NC pins — Table 4-1's `NC` row has an em dash in the PIN NO. column, so it
belongs only to PW/FK (Table 4-2). No `no_connect` pin entries were created.

---

## 1. Disagreements with the official KiCad library

Symbol: `TLC555xD` in `/usr/share/kicad/symbols/Timer.kicad_sym`. It is a
`(extends "NE555D")` leaf with **no pins of its own**, so the 8 pins come from the parent
`NE555D`. Footprint: `Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod`.

### Pin disagreements (4)

| # | Pin | Datasheet says | KiCad `NE555D` says | Decision | Page |
|---|---|---|---|---|---|
| K1 | 4 | `RESET`, no overbar; TYPE `Input`; "Active low reset input forces output and discharge low." | name `~{RST}` (overbar), type `input` | **Datasheet wins** — gold `name` is `RESET`, plain. Both the Figure 4-1 pinout and the Table 4-1 NAME column print `RESET` with no bar; only the description says "active low". KiCad's `~{RST}` is the NE555 family's legacy rendering. Type agrees. | 3 |
| K2 | 5 | `CONT`, TYPE **`Input`**, "Controls comparator thresholds. Outputs 2/3 VDD and allows bypass capacitor connection." | type **`open_collector`** | **Datasheet wins** — gold `CONT` is `input`. The TYPE column is explicit, and the word "Outputs" in the description refers to the internal 2/3 V<sub>DD</sub> reference node that CONT *sets*, not to a driver this pin contains. KiCad's `open_collector` is a 555 pin-5 legacy (the bipolar NE555 draws a discharge transistor at pin 5; the CMOS TLC555 does not). Type/status: `extracted` (read straight from a printed TYPE cell). | 3 |
| K3 | 7 | `DISCH`, TYPE **`Output`**, "**Open collector** output to discharge timing capacitor." | type **`input`** | **Datasheet wins** — gold `DISCH` is `open_collector`, status `inferred` (that is the explicit open-drain/open-collector row of `reference.md`, which requires the `inferred` flag). KiCad's `input` is simply the opposite of what the datasheet prints. | 3 |
| K4 | 8 | `VDD` (V with subscript DD), TYPE `—`, "Power-supply voltage." | name `VCC` | **Datasheet wins** — gold `name` is `VDD`. This is TI's own supply naming on this part, not an abbreviation; `pdftotext` and KiCad both flatten the subscript to plain letters. Type agrees (`power_in`, via the supply-pin rule, status `inferred`). | 3 |

### Dimension / footprint disagreements (2)

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| D1 | `land_pad_length` | `8X (.061 )` **[1.55] mm**, reference value | pad size **1.95 × 0.6 mm** | **Datasheet wins** — gold `land_pad_length` = 1.55 (nom). KiCad's pads are IPC-7351 nominal-density generated, which deliberately makes them longer than TI's land pattern. This is the anticipated pad-SIZE difference, not an error. | 39 (repeated identically on p. 40) |
| D2 | `land_span` | `(.213)` **[5.4] mm**, reference value | pads at x = ±2.475 → **4.95 mm** centre-to-centre | **Datasheet wins** — gold `land_span` = 5.4 (nom, status `inferred`). Same IPC-7351-vs-TI-land-pattern cause as D1. | 39 (repeated on p. 40) |

### Agreed (checked, no disagreement)

| Item | Datasheet | KiCad | Page |
|---|---|---|---|
| pad count / pin count | 8 | 8 | 3 / footprint |
| pitch | `6X .050` [1.27] | pad y = ±1.905, ±0.635 → 1.27 mm | 38, 39 |
| body size | 4.81–5.00 × 3.81–3.98 mm (nom 4.9 × 3.9) | footprint name `3.9x4.9mm` | 38 |
| `land_pad_width` | `8X (.024)` [0.6] | 0.6 mm | 39 |
| overall lead-tip width | `.228-.244` [5.80-6.19] | KiCad stores no lead-span value (its ±3.7 mm is the **courtyard**, 7.4 mm total, not the lead span) | 38 |

Net: **6 disagreements (K1–K4, D1–D2).** All four pin disagreements and both dimension
disagreements were decided in favour of the datasheet, in each case with a printed statement on
page 3 or page 39 that says so directly. Three of the four pin disagreements (K2, K3, K4) are
not abbreviation differences at all: KiCad's `NE555D` parent is a shared NE555-family symbol and
carries two pin types and one supply name that this datasheet contradicts.

Generated result: symbol pins exactly as tabled above; footprint `SOIC-8_3.9x4.9mm_P1.27mm` with
8 roundrect pads, 1.27 mm pitch, x = ±2.7 (5.4 mm span), pad size 1.55 × 0.6 mm — all three of
those pad figures taken from the datasheet land pattern, not from KiCad.

---

## 2. Values I had to interpret

1. **`mpn` = `TLC555xD`.** The datasheet's own orderable SOIC-8 numbers are `TLC555CD`,
   `TLC555ID`, `TLC555QD`, `TLC555QDR`, `TLC555QDRG4` (page 30, PACKAGE OPTION ADDENDUM);
   there is no bare "TLC555" in SOIC. `x` is TI's grade wildcard (C/I/Q), so `TLC555xD` is
   "TLC555, any grade, D (SOIC-8) package" and lines up 1:1 with the KiCad symbol name.
   `TLC555CD` is the substitution if a literal orderable number is preferred. (Same reasoning as
   `INA219AxD` in `ina219_soic8`; `lm358_soic8` uses the bare `LM358` because LM358 is orderable
   without a package suffix — that is why the golds differ.)
2. **`CONT` is `input`, not an output (page 3).** Its description says "Outputs 2/3 VDD"; I read
   that as describing the internal threshold reference the pin *controls*, because the printed
   TYPE cell says `Input` and the pin is driven from outside in every application figure
   (page 19 shows a "Modulation Input" arrow into CONT). This is the one interpretive call that
   changes a KiCad-matching outcome, so it is flagged for the reviewer.
3. **`VDD` name (page 3).** Printed with DD as a subscript; `pdftotext` and KiCad both yield
   `VDD`, so no subscript handling was needed.
4. **`land_span` marked `inferred` (page 39).** `(.213) [5.4]` is printed with no label; on the
   render the arrow spans pad-1 centreline to pad-5 centreline, i.e. centre-to-centre between
   the two pad rows. That identification is an interpretation, hence `inferred` — the same call
   and the same status as `lm358_soic8` and `ina219_soic8`, which cite the identical JEDEC
   drawing `D0008A`.
5. **Which axes `overall_width` / `body_length` / `body_width` measure (page 38).** Fixed from the
   rendered top and bottom views: the `.228-.244` arrow runs across the lead rows (→ `overall_width`),
   `.189-.197` runs along them (→ `body_length`), `.150-.157` is the width across between the rows
   (→ `body_width`). Because assigning each printed range to a named dimension required reading which
   axis its arrow runs along, all three are marked `inferred` rather than `extracted` — the same call,
   and for the same reason, as `land_span` above. Same drawing, same convention as the `lm358_soic8`
   and `ina219_soic8` golds.
6. **`lead_length` `.016-.050 [0.41-1.27]` (page 38, DETAIL A).** Marked `extracted`: the DETAIL A
   arrow runs from the body edge to the lead tip at the seating plane, confirmed on the render.
   Consistent with the two existing SOIC-8 golds, which extract the identical callout.
7. **`group` = `"power"` on GND and VDD.** `reference.md` lists `power` as a permitted group for
   supply pins, and `lm358_soic8` uses it for V−/V+. `ina219_soic8` omits `group` entirely on a
   single device. Either is defensible; the gold follows `lm358_soic8` because this is likewise a
   two-supply part. No `A`/`B` units exist — the TLC555 is a single timer, so the `TRIG`/`THRES`
   inputs are not units.
8. **No `alt_names` anywhere.** `DISCH`'s "Open collector output …" is a *type*, not a second
   function, and `CONT`'s "Outputs 2/3 VDD" is a description; per `reference.md` a description is
   not an alternate function.
9. **Status flags.** 5 pins `extracted` (2 TRIG, 3 OUT, 4 RESET, 5 CONT, 6 THRES — number and name
   read from Figure 4-1 / Table 4-1, type read from a printed TYPE cell). 3 pins `inferred`
   (1 GND and 8 VDD → `power_in` via the supply/ground rule; 7 DISCH → `open_collector` via the
   open-drain rule). 6 dimensions `extracted` (pitch, height, lead_width, lead_length,
   lead_thickness, standoff — each read straight from a printed callout), 4 `inferred`
   (`overall_width`, `body_length`, `body_width` per item 5 above, and `land_span`). Nothing marked
   `confirmed`.

---

## 3. Dimensions deliberately left out

All on page 38, PACKAGE OUTLINE `D0008A`:

| Callout | What it appears to be | Why omitted |
|---|---|---|
| `2X .150 [3.81]` | row-to-row centre-to-centre span of pins 1 and 4 (= 3 × pitch) | no `reference.md` dimension name covers the *outline* row span (`land_span` is defined as coming from the land pattern only); also redundant with the pitch. |
| `.010 [0.25]` ⌖ C A B | lead seating-plane / coplanarity tolerance, referenced to datums C, A, B | no dimension name; it is a positional tolerance, not a size. |
| `.004 [0.1] C` | PIN 1 ID AREA offset to datum C | feature of the pin-1 marker, not a package size. |
| `(.041) [1.04]`, `0°–8°`, `4X (0°–15°)`, `R …` | DETAIL A reference length, foot angles, foot radius | no matching dimension name / not a package size. |

Page 39 / 40 (land pattern and stencil design): `(R.002 ) TYP [0.05]` (pad corner radius),
`.0028 MAX [0.07]` and `.0028 MIN [0.07]` (solder-mask tolerance, all around) — no dimension
names for pad corner geometry or mask tolerances.

Note 3 on the outline ("Mold flash … shall not exceed `.006 [0.15]` per side") is a note, not a
dimensioned callout, and was not extracted.

---

## 4. Datasheet self-contradictions

**None found.** Checks made:

- Figure 4-1 (p. 3) top view, Table 4-1 PIN NO. column (p. 3), the simplified schematic (p. 1),
  Figure 6-1 (p. 13) and the PWM application figure (p. 19) all give the same number for all
  eight pins: no pin carries a different number anywhere in the document.
- The PW (TSSOP-14) and FK (LCCC-20) pinouts on p. 3 are internally consistent (Table 4-2's
  PW/FK number columns match Figures 4-2 and 4-3); they were checked only to confirm that the
  D package has no NC pins, not used as data.
- The outline (p. 38, drawing `4214825/C 02/2019`) and the land pattern (p. 39, same drawing
  number and same `SOIC - 1.75 mm max height` title) agree on pitch (`6X .050` [1.27] vs
  `6X (.050 )` [1.27]). The stencil design on p. 40 repeats the p. 39 land values identically.
- The `SOIC (D) | 8` entry in the page-30 PACKAGE OPTION ADDENDUM matches the D-package figure
  and `package.pin_count` = 8.

Two things that are *not* contradictions of any value used here, but are worth recording:

- Page 1's package table lists `SOIC (8) 4.9mm × 6.0mm` as a nominal size "including pins",
  while the outline gives a lead span of 5.80–6.19 mm. 6.19 rounds coarsely to "6.0" on the
  feature page; the outline dimension is the controlled one and is what the gold uses.
- The datasheet header is stamped `REVISED JANUARY 2026` and the copyright line reads 2026, but
  the mechanical drawing is stamped `02/2019`. Neither affects any extracted value; the
  SHA-256 in `spec.gold.json` is of the PDF actually used and matches `source.txt`.

---

## 5. Tool results

```
kicad-partspec validate spec.gold.json --datasheet tlc555.pdf   ->  passed: true  (0 failures, 7 warnings)
kicad-partspec build    spec.gold.json --out out --concise     ->  passed: true  (0 failures, 7 warnings)
```

All 7 warnings are `status.inferred` (pins 1, 7, 8 and the dimensions `overall_width`,
`body_length`, `body_width`, `land_span`) — the deliberate honesty flags, not defects. Files written:
`out/TLC555xD.kicad_sym` and `out/partspec.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod`.
No `footprint.skipped` warning: the datasheet does carry a complete example land pattern, so
the footprint was generated.