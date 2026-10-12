# PCA9306DCU (VSSOP-8, drawing DCU0008A) — review

Datasheet: `./pca9306.pdf`, sha256 `1cd97c734729f2bfca26ccaa93521c04c373568e4ebe6d892267dba2571e21e6`,
SCPS113O (Rev. O, September 2023). 38 PDF pages. Pin table on PDF page 4, package outline on
PDF page 31, land pattern on PDF page 32 — every pin and every dimension below was checked on the
rendered image of those pages, not only in the text layer.

## 1. Disagreements with the official KiCad library

| Item | Datasheet (DCU0008A) | KiCad | Decision |
|---|---|---|---|
| Footprint identity | `VSSOP - 0.9 mm max height`, 8 leads, pitch 0.5 mm (p.31) | `VSSOP-8_3x3mm_P0.65mm.kicad_mod` was named in the task; the PCA9306 symbol's own `ki_fp_filters` lists `VSSOP*2.3x2mm*P0.5mm*` | Compared against `VSSOP-8_2.3x2mm_P0.5mm.kicad_mod`, the footprint the KiCad symbol itself selects for this part. The 3x3/P0.65 footprint is a different package (0.65 mm pitch); the datasheet's 0.5 mm pitch rules it out (p.31). Not a value disagreement. |
| Pitch | `6X 0.5` (basic, boxed), p.31 and p.32 | 0.5 mm (pads at y = −0.75, −0.25, 0.25, 0.75) | Agree. |
| Body size | 2.2–2.4 mm across rows × 1.9–2.1 mm along rows (p.31) | body 2.3 × 2.0 mm nominal (IPC-7351 mid-tolerance of the same window) | Agree; nothing to change. |
| Lead span | 3.0–3.2 mm tip-to-tip across rows (p.31) | courtyard/pad reach ±2.025 mm ⇒ 4.05 mm | Different quantity (courtyard/pads vs lead tips); the datasheet value is the package outline and is kept as `overall_width`. Not a contradiction. |
| Land pad size | `8X (0.85)` × `8X (0.3)`, reference values (p.32) | pads 1.25 × 0.35 mm | Datasheet wins for the generated footprint: `land_pad_length` 0.85, `land_pad_width` 0.3. KiCad pads come from IPC-7351, a legitimate difference. |
| Land span | `(3.1)` between pad-row centrelines (p.32) | pad rows at x = ±1.4 mm (span 2.8) | Datasheet wins: `land_span` 3.1. Built footprint has pads at x = ±1.55. |
| Pin 1 GND type | I/O column `—` | `power_in` | Agree (skill: ground pin → `power_in`, status `inferred`). |
| Pins 2, 7 VREF1/VREF2 type | I/O column `I`, "reference supply voltage" | `power_in` | Agree: they are supply pins, so `power_in` even though the column says `I`. |
| Pin 8 EN type | `I`, "Switch enable input" | `input` | Agree. |
| Pins 3, 4, 5, 6 SCL1/SDA1/SDA2/SCL2 | `I/O` | `bidirectional` | Agree. |
| Pin names/numbers 1–8 | Table 5-1 and Figure 5-2 | identical (no `extends`) | No disagreement at all: 8/8 names and numbers match KiCad exactly. |

The only disagreements are the three land-pattern numbers (pad size, pad row spacing) and the
package-outline dimension the task pointed at, all decided for the datasheet, which is why the
built footprint is `VSSOP-8_2.3x2.0mm_P0.5mm` with 0.85 × 0.3 pads at ±1.55 rather than a byte copy
of the KiCad file.

## 2. Values that had to be interpreted

- **Package family `VSSOP`.** The datasheet has four packages: DCT (SSOP-8, p.29–30), **DCU
  (VSSOP-8, p.31–33)**, DQE (X2SON-8, p.34–36) and YZT (DSBGA-8). Only the DCU drawing is used.
  The task asks for VSSOP, so `family: "VSSOP"`, and the orderable parts table (p.28) confirms
  `PCA9306DCUR/DCUT` = VSSOP = DCU = 8 pins.
- **`overall_width` = 3.0–3.2 (`3.2` over `3.0 TYP`).** It is the largest across-rows dimension and
  its extension lines land on the outer tips of leads 1 and 8, so it is tip-to-tip, not the body.
  Checked by measuring the rendered page: tip-to-tip 770 px, body 570 px, ratio 1.35 = 3.2/2.4.
- **`body_width` = 2.2–2.4** (the dimension with datum B, extension lines on the body edges) and
  **`body_length` = 1.9–2.1** (the left-hand vertical dimension along the pin rows, whose
  extension lines coincide with the outer edges of leads 1 and 4). The two are easy to swap on this
  drawing because the package is nearly square; pixel measurement on the render gives 570 px across
  the rows and 493 px along them, matching 2.4 : 2.1.
- **`lead_length` = 0.20–0.35** from Detail A: the flat foot between the tip and the body wall,
  measured to the seating plane. This is the foot, not the body-to-tip length (the drawing gives no
  body-to-tip length).
- **`height` = 0.6–0.9** and **`standoff` = 0.0–0.1**, both in Detail A. The stacked `0.9`/`0.6` pair
  runs from the seating plane (datum C) to the top of the moulding, so `height` gets `min`/`max`
  rather than `max` only.
- **`lead_thickness` = (0.13) TYP**, the only thickness callout on the sheet: in the front view it
  straddles the lead at the tip, so it is the lead thickness. It is a reference value in
  parentheses with no tolerance; marked `inferred` for that reason, and it does not affect the
  generated files.
- **`land_span` = (3.1)**, the bracketed reference dimension between the two pad-row centrelines on
  the land pattern (p.32). Marked `inferred` because the drawing does not name it.
- **Pin types.** `EN` is `input` (printed `I`, "Switch enable input"). `VREF1`/`VREF2` are printed
  `I` as well, but they are reference *supply* pins, so they are `power_in` with status `inferred`,
  as is `GND` (printed `—`). The four bus pins are `bidirectional` from the printed `I/O`.
- **No `group`.** The datasheet shows two voltage sides of one translator; per the skill the two
  sides of one function are not units, so nothing is grouped (this is the same situation as the
  TXS0108E gold case).
- **`body_thickness` omitted** — the DCU drawing gives no body height separate from the 0.6–0.9
  overall height.

## 3. Things in the datasheet that could mislead

- **The feature list (p.1) calls the bus pins "Open-drain I2C I/O ports (SCL1, SDA1, SCL2, and
  SDA2)", and "High-impedance SCL1, SDA1, SCL2, and SDA2 pins for EN = low".** An extractor could
  type these four `open_collector` or `tri_state`. Neither is right for the pin itself: Table 5-1
  prints `I/O`, and the device is a bidirectional pass switch (RON = 3.5 Ω) that drives both ways
  while enabled, so `bidirectional` is what both Table 5-1 and KiCad say.
- **Four packages, one pin table.** Table 5-1 has a numbered column for `DCT, DCU, DQE` and a
  ball column for `YZT` (`A1`…`D2`). Figure 5-4 (YZT) shows 1/2 and A/B/C/D rows; only the
  DCT/DCU/DQE numbering is used here, and the same eight names appear in every package figure.
- **Drawing revision dates do not match the document revision.** The document is Rev. O
  (September 2023), but the SSOP drawing in this revision is stamped `4220784/D 10/2025` while
  the DCU drawing still reads `4225266/A 09/2014`, and the PDF's own creation date is 2026-07-16.
  Nothing in the DCU drawing conflicts with the pin table.
- **The drawing title says "VSSOP - 0.9 mm max height"** and the outline gives 0.6–0.9; consistent.

## 4. Build result

`kicad-partspec validate spec.gold.json --datasheet pca9306.pdf` passes (only the 5 expected
`status.inferred` warnings: pins 1, 2, 7; dimensions `lead_thickness` and `land_span`).
`kicad-partspec build --out out --concise` passes with 0 failures and produces
`PCA9306.kicad_sym` plus the footprint `VSSOP-8_2.3x2.0mm_P0.5mm.kicad_mod` (8 pads, 0.85 × 0.3,
pitch 0.5, row centres ±1.55) built from the datasheet land pattern on p.32.