# TPS5430DDA — gold PartSpec review

Datasheet: `tps5430.pdf`, SHA-256 `88c98e6e51851285fbbfc17837d002b29af7cd3fe30442fa7e4612c5179985da`
(SLVS632L – JANUARY 2006 – REVISED APRIL 2026, i.e. Rev. L, April 2026).
Deliverable: `spec.gold.json` — `validate` passes (only the six expected `status.inferred` warnings),
`build` passes and generates both a symbol and a 9-pad footprint.

Everything below was checked on rendered pages (`pdftoppm -r 150` and `-r 400` crops), not on the text layer alone.

---

## 1. KiCad disagreements

Cross-check sources: `/usr/share/kicad/symbols/Regulator_Switching.kicad_sym` (symbol `TPS5430DDA`, no `extends`)
and `/usr/share/kicad/footprints/Package_SO.pretty/SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.514x3.2mm.kicad_mod`.

### Symbol

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| 1 | pin 1 `BOOT` electrical type | TYPE column `O`, footnote "I = input, O = output" (and "Output voltage BOOT to PH" in the Absolute Maximum table) | `input` | **Datasheet wins → `output`, `extracted`.** The printed TYPE column is explicit; the skill's table maps `O` to `output`. | 3 (also 4) |
| 2 | pin 8 `PH` electrical type | TYPE column `I` | `output` | **Datasheet wins → `input`, `extracted`.** Page 3's TYPE column prints `I`. (Page 4 calls PH an "Output voltage" — see contradiction C2 below; page 3 is the pin table, which is the reference's source for pin types.) | 3 |
| 3 | pin 5 name | `ENA` | `EN` | **Datasheet name kept (`ENA`).** KiCad's `EN` is an abbreviation of the same primary function, not a different pin. | 3 |
| 4 | pin 9 name | `DAP` (pin table row "DAP"; the name is used in Figure 4-1, in the layout text on p23 and in the drawings) | `GNDPAD` | **Datasheet name kept (`DAP`).** `GNDPAD` is KiCad's own convention for the thermal pad. | 3 |
| 5 | pin 9 number | Pin table prints "—" (no number); the package outline bottom view (p38) and the land pattern (p39) both label the exposed pad `9` | `9` | **Agree → `9`, but `inferred`**, because the pin table itself gives no number and the number `pin_count + 1` comes from the drawing / the convention. | 3, 38, 39 |
| 6 | pins 2, 3 | "Not connected internally", TYPE `—` | `no_connect`, hidden | **Agree → `no_connect`.** | 3 |
| 7 | pins 4, 6, 7 | `VSENSE` = `I`; `GND` = "Ground. Connect to DAP."; `VIN` = "Input supply voltage." | `input`, `power_in`, `power_in` | **Agree.** GND/VIN are `power_in`, status `inferred`. | 3 |

### Footprint

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| 8 | pad count / exposed pad | 8 leads + exposed thermal pad (DAP) | 9 pads, pad 9 rect at origin | **Agree.** | 38, 39 |
| 9 | pitch | `6X 1.27` (outline) and `6X (1.27)` (land) | 1.27 (y = −1.905, −0.635, 0.635, 1.905) | **Agree.** | 38, 39 |
| 10 | pad row spacing | land span `(5.4)` centre-to-centre | pads at x = ±2.6375, i.e. 5.275 | **Datasheet wins → `land_span` 5.4**, giving pads at x = ±2.7 in the generated footprint. 0.125 mm (2.4%) per side; KiCad's value is IPC-7351-derived, not from this datasheet. | 39 |
| 11 | pad size | `8X (1.55)` × `8X (0.6)` | 1.625 × 0.6 | **Datasheet wins → 1.55 × 0.6.** Pad size is explicitly allowed to differ (IPC vs. datasheet land pattern); the width already agrees exactly. | 39 |
| 12 | body size | 3.8–4.0 across the rows, 4.8–5.0 along them (midpoints 3.9 × 4.9) | F.Fab outline 3.9 × 4.9 | **Agree.** | 38 |
| 13 | exposed pad | land pad 2.71 × 3.40 mm (rectangular) | pad 9 = 2.514 × 3.20 mm | **Datasheet wins**, but see interpretation I3: the PartSpec field holds one number, so the limiting axis (2.71) is recorded and the builder emits a 2.71 × 2.71 square pad. KiCad's 2.514 × 3.2 is IPC nominal and smaller on both axes. | 38, 39 |
| 14 | symbol footprint field | — | `Package_SO:TI_SO-PowerPAD-8_ThermalVias` | Not a pin or dimension disagreement; recorded here only because the generic `SOIC-8-1EP` footprint was used for this cross-check instead. | — |

Items 5, 6, 7, 8, 9 and 12 above are agreements (checked, not assumed). The genuine disagreements are
items **1, 2, 3, 4** (pin) and **10, 11, 13** (geometry): **7 in total**.

---

## 2. Values that had to be interpreted

| # | Value | Why it needed a judgement call |
|---|---|---|
| I1 | `package.family` = `SOIC` | The datasheet names the package three ways: "8-pin **SOIC** PowerPAD integrated circuit package" (p1, Description), "**HSOIC** With Thermal Pad" (Figure 4-1 title, p3), "**SO** PowerPAD (DDA)" (ordering tables), and "PowerPAD™ **SOIC**" (generic package view, p34). `SOIC` is used because it is the term the datasheet's own description uses and the one the target KiCad footprint is named for; `HSOIC` is TI's internal name for DDA and is not a KiCad footprint family. |
| I2 | `mpn` = `TPS5430DDA` | The datasheet covers TPS5430 and TPS5431 in the one DDA package; the only KiCad symbol is `TPS5430DDA`, which is also the orderable part number for the TPS5430 in this package. |
| I3 | `ep_size` (2.11–2.71) and `land_ep_size` (2.71) | The exposed pad is **rectangular**, and a PartSpec dimension holds a single number. The recorded pair is the axis across the 3.9 mm body direction (2.11–2.71 outline, 2.71 land). The other axis is 2.8–3.4 (outline, p38) and 3.4 (land, p39). The choice was made so that the land pad equals the EP maximum, which is exactly how TI sizes it (the discarded DDA0008J drawing shows the same relation, 2.6 land = 2.6 EP max). Both are marked `inferred`. |
| I4 | `land_ep_size` = the green "SOLDER MASK DEFINED PAD" rectangle, not the dashed rectangle | The land pattern prints four numbers around the exposed pad: `(2.95)` and `(4.9)`, both tagged **NOTE 9**, plus `(2.71)` and `(3.4)`, tagged **SOLDER MASK DEFINED PAD** / **SOLDER MASK OPENING**. Checked on the rendered page: the `(2.95)`/`(4.9)` dimensions belong to the dashed rectangle that the leader labels "METAL COVERED BY SOLDER MASK", and NOTE 9 says "Size of metal pad may vary due to creepage requirement" — that is the surrounding ground pour, not a pad dimension. The `(2.71)`/`(3.4)` dimensions belong to the solid rectangle labelled "SOLDER MASK DEFINED PAD", which is the exposed pad. Only `(2.71)` is recorded. |
| I5 | `lead_length` 0.40–1.27 from the stacked pair in Detail A | Detail A prints `1.27` over `0.40` on one arrow span (body fillet to lead toe). Per the reference's "two numbers stacked gets min and max" rule this is recorded as min 0.40, max 1.27 — the same reading the `lm358_soic8` gold gives for the identical D0008A pair `[0.41-1.27]`. The foot is the 0.40 end. |
| I6 | `lead_thickness` 0.10–0.25 | The middle side view prints `0.25 TYP` over `0.10` with arrows across the lead toe. The two-number rule was applied (min 0.10, max 0.25); `TYP` on the upper number was not turned into `nom`. Nothing in the generated files depends on it. |
| I7 | `overall_width` min 5.8 / max 6.2 | The top view spans lead tip to lead tip across the rows with `6.2 TYP` over `5.8` (the render puts `TYP` on 6.2's line). This is one of the sheet's plain stacked pairs, like `5.0/4.8`, `4.0/3.8`, `0.51/0.31` and `2.71/2.11`, so the two-number rule applies and the pair is recorded as min 5.8, max 6.2. |
| I8 | `land_span` 5.4 marked `inferred` | The `(5.4)` dimension has no label; the rendering shows it spanning the two pad-row centre lines. Marked `inferred` for the same reason the `lm358_soic8` gold marks its `land_span`. |
| I9 | `2X 3.81` on the outline was **left out** | On the rendered page the `2X 3.81` arrows run from the pin-8 centreline to the pin-5 centreline, i.e. three pitches — it repeats the pitch rather than dimensioning a new feature. The reference says a lead centre-to-centre span is not recorded and that an unclear number is better left out. Same for the boxed `0.25` gage plane, the `0.1`/`0.25 Ⓜ` position-tolerance frames, `4X (0°-10°)` lead toe angle, `Ø0.2 TYP` via, `(1.3) TYP` via pitch and `(0.07 MAX/MIN)` mask expansion. |

## 3. Contradictions inside the datasheet

**C1 — Two different package drawings for the same DDA package, with no statement of which is current.**
The mechanical pages carry six DDA0008 sheets:

| Sheet | Drawing code | Stamp | EP (outline) | EP (land pattern) |
|---|---|---|---|---|
| p35 outline / p36 land / p37 stencil | `DDA0008J` | `4221637/B 03/2016` | 2.0–2.6 × 2.5–3.1 | 2.6 × 3.1 |
| p38 outline / p39 land / p40 stencil | `DDA0008B` | `4214849/B 09/2025` | 2.11–2.71 × 2.8–3.4 | 2.71 × 3.4 |

Every other dimension is identical between the two (pitch 1.27, body 4.8–5.0 × 3.8–4.0, 6.2 TYP/5.8,
1.7 MAX, 8X 0.51/0.31, 0.25 TYP/0.10, 1.27/0.40, 0.15/0.00, and the whole land pattern except the exposed pad).
`DDA0008B` adds the `4X (0°-10°)` lead toe angle, drops "variation BA" from the JEDEC MS-012 reference,
and numbers the exposed pad `9` in the bottom view; `DDA0008J` does not number it.
**Resolution: `DDA0008B` (p38/p39) was used**, on the grounds that its stamp (09/2025) is the most recent in the
document and closest to this revision (April 2026), and it is the only sheet that numbers the exposed pad,
which this part has. The counter-argument — that `J` is the higher revision letter of the `DDA0008` drawing
series — is not decisive, because the drawing document numbers run the other way (`4214849` < `4221637`).
If a human decides `DDA0008J` is current, only two entries change: `ep_size` → 2.0–2.6 and
`land_ep_size` → 2.6. Nothing else in the gold is affected.

**C2 — PH is typed `I` in the pin table and called an "Output voltage" in the absolute-maximum table.**
Page 3, Table 4-1 prints `PH 8 I`; page 4 lists "Output voltage PH to GND (Steady-state)" and "Source current PH"
under output/source headings. `BOOT` is consistent (`O` on p3, "Output voltage BOOT to PH" on p4).
Resolution: the pin table (p3) governs electrical types, so `PH` is `input`; the contradiction is recorded here.

**C3 — The exposed pad has no pin number in the pin table but is numbered `9` in the drawings.**
Page 3 prints "—" in the NO. column for `DAP`; page 38 (bottom view) and page 39 (land pattern) both print `9`
beside the pad. Resolution: number `9` used, status `inferred`, quoted from page 3 — which is what the
reference prescribes for an exposed pad the pin table leaves unnumbered.

**C4 — Package naming.** "SOIC PowerPAD" (p1, p34), "HSOIC With Thermal Pad" (p3) and "SO PowerPAD" (ordering
tables) all name the same DDA package. See I1.

---

## Report

- **Pins:** 9 entries — 8 leads (BOOT 1, NC 2, NC 3, VSENSE 4, ENA 5, GND 6, VIN 7, PH 8) plus the exposed pad
  `DAP` as pin 9. 6 are `inferred` (GND, VIN, DAP — supply/ground/no-number mapping), 6 `extracted`.
- **Dimensions:** 14 — pitch, overall_width, body_length, body_width, height, lead_width, lead_thickness,
  lead_length, standoff, ep_size (outline) and land_pad_length, land_pad_width, land_span, land_ep_size
  (example land pattern). 11 `extracted`, 3 `inferred`.
- **Footprint generated:** yes. `out/partspec.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod` with 9 pads
  (8 roundrect 1.55 × 0.6 at x = ±2.7, y = ±1.905/±0.635, plus a 2.71 × 2.71 rect exposed pad at the origin).
  (`kicad-partspec` omits the `-1EP` infix from the *name* of dual-row footprints; the pad is present.)
- **KiCad disagreements:** **7** — four at pin level (BOOT type `output` vs KiCad `input`; PH type `input`
  vs KiCad `output`; `ENA` vs KiCad `EN`; `DAP` vs KiCad `GNDPAD`) and three at geometry level
  (land span 5.4 vs 5.275; pad length 1.55 vs 1.625; exposed pad 2.71 × 3.4 vs 2.514 × 3.2). Every one was
  decided on a rendered datasheet page and the datasheet won each time; the two name items are KiCad
  abbreviations of the same primary function. The remaining nine checked items (pin numbers 1–9, pad count,
  pitch, body size) agree.

---

## Round-4 corrections

One correction, to `overall_width` (page 38, quote `6.2 TYP SEATING PLANE 5.8`):

- **Was:** `"nom": 5.8, "max": 6.2`.
- **Now:** `"min": 5.8, "max": 6.2`. Page, quote and `status: extracted` are unchanged.

Why: 6.2 over 5.8 is lead tip to lead tip across the rows, and it is one of the sheet's plain stacked
max/min pairs — the same shape as `5.0/4.8` (body length), `4.0/3.8` (body width), `0.51/0.31`
(lead width) and `2.71/2.11` (exposed pad) — so it takes the two-number rule, min then max. The
previous reading made 5.8 a nominal equal to the lower limit of its own range, which no convention
supports, and the midpoint 6.0 is printed nowhere on the sheet.

The original I7 prose also mis-stated the page: it read the callout as `6.2` over `5.8 TYP`, while
the render puts `TYP` on 6.2's line. I7 has been corrected to match the render; either way 5.8 is
the lower limit, not a nominal, so the recorded values do not change with the fix.

Nothing else in the spec was touched. The generator does not read `overall_width`, so the generated
symbol and footprint are byte-identical before and after; the lead-coverage check is the only reader
of this dimension, and it takes the nominal — or, with no nominal, the midpoint of min/max — which
moves the lead tip from 2.90 to 3.00 and changes no finding. Both variants build with the same six
`status.inferred` warnings.