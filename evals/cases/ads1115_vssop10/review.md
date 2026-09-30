# Review — ADS1115IDGS, TI DGS (VSSOP-10), datasheet SBAS444E

Datasheet: `./ads1115.pdf`, sha256 `eefff4d412ce2dcd7e659f47238edc9b2fa02e5971f2625af730502033701834`
(confirmed against `source.txt`).

Pages used: p.3 (Table 4-1 Pin Functions + Figure 4-2 DGS/DYN top view), p.51 (DGS0010A
package outline), p.52 (DGS0010A land pattern). Every pin pairing and every dimension
callout was checked on a rendered page image (150 dpi for the pinout, 400-600 dpi crops for
the package drawing).

## KiCad cross-check

Sources:
- Symbol `ADS1115IDGS` in `Analog_ADC.kicad_sym` — it `extends "ADS1015IDGS"`, so all ten
  pins live in the parent symbol.
- Footprint `Package_SO:TSSOP-10_3x3mm_P0.5mm`.

### Disagreements

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| 1 | Pin 2 `ALERT/RDY` electrical type | Type column: "Digital output"; description: "**Open-drain output.** Connect to VDD using a pullup resistor." | `output` | **Datasheet.** `open_collector`, status `inferred`. The datasheet states open-drain explicitly and the skill's type table maps "open drain / open collector output" to `open_collector`. | 3 |
| 2 | `land_pad_length` | `10X (1.45)` = 1.45 mm | pad `size 1.1 0.25` → 1.1 mm | **Datasheet.** Land-pattern pad geometry comes only from the datasheet's example land pattern. | 52 |
| 3 | `land_pad_width` | `10X (0.3)` = 0.3 mm | 0.25 mm | **Datasheet.** Same reason. | 52 |
| 4 | `land_span` (row spacing) | `(4.4)` centre-to-centre = 4.4 mm | pads at `x = ±2.15` → 4.3 mm | **Datasheet.** 4.4 mm. | 52 |
| 5 | `package.family` | "DGS (**VSSOP**, 10)" (p.1) and "**VSSOP** - 1.1 mm max height" (p.51) | footprint named `TSSOP-10_3x3mm_P0.5mm` | **Datasheet.** `family: "VSSOP"`. Both names are dual-row families in the tool, so the generated geometry is identical; only the footprint name differs. | 1, 51 |

### Agreements (checked, no disagreement)

- Pin count 10, pad count 10.
- Every pin number and every pin name: `1 ADDR, 2 ALERT/RDY, 3 GND, 4 AIN0, 5 AIN1,
  6 AIN2, 7 AIN3, 8 VDD, 9 SDA, 10 SCL` — identical to KiCad.
- Types `AIN0-3 = input`, `ADDR = input`, `SCL = input`, `SDA = bidirectional`,
  `GND = power_in`, `VDD = power_in` — identical to KiCad.
- Pin 1 at the top-left of the left column — matches Figure 4-2 (pin 1 upper left).
- Pitch 0.5 mm — agrees (datasheet `8X 0.5`, KiCad pads at 0.5 mm steps).
- Body 3.0 × 3.0 mm — agrees within the datasheet's 2.9-3.1 mm limits (KiCad fab outline ±1.5).
- `mpn` `ADS1115IDGS` — same string as KiCad's symbol Value.
- Not comparable: KiCad's courtyard (±2.95 × ±1.8) and reference/silk placement are
  KiCad constructs, not datasheet dimensions. Pad corner radius `(R0.05) TYP` (p.52) has no
  dimension name in the reference and was left out.

## Values that had to be interpreted

1. **`overall_width` = 4.75 / 5.05** — the top view prints `5.05` over `4.75` with `TYP`
   centred between them, which is TI's stacked min/max-with-TYP format, so it is read as a
   range, not as a typ value. The dimension arrows, checked on the 400 dpi render, run from
   the left lead tips to the right lead tips, i.e. across the two pin rows, which is
   `overall_width` for a dual-row part. Corroborated by p.1, which lists the DGS package as
   "3.00mm × 4.90mm" — the 3.00 nominal body and the 4.90 nominal of this very dimension.
   No `overall_length` (tip to tip along the pin rows) is dimensioned anywhere in DGS0010A,
   so none is recorded.
2. **`body_length` vs `body_width`** — in the top view the pin rows run vertically (pins
   1-5 in the left column, 6-10 in the right), so the vertical callout **A** (`3.1 / 2.9
   NOTE 3`, note 3 = excludes mold flash) is `body_length` and the horizontal callout **B**
   (`3.1 / 2.9 NOTE 4`, note 4 = excludes interlead flash) is `body_width`. Both print
   2.9-3.1, so the assignment does not change either number.
3. **`standoff` = 0.05 / 0.15** — Detail A prints `0.15 / 0.05` with no name. The 600 dpi
   crop shows the upper extension line lined up with the body underside and the lower one
   with the seating plane, so it is the gap between the seating plane and the body bottom.
   Marked `inferred` because the drawing does not label it.
4. **`lead_length` = 0.4 / 0.7** — Detail A prints `0.7 / 0.4`; the dimension runs from the
   lead toe to the point where the lead leaves the body wall, i.e. the foot length. Marked
   `inferred` for the same reason.
5. **`lead_thickness` = 0.13 / 0.23** — `0.23 TYP / 0.13`, measured across the lead in the
   side view. The `TYP` sits between the two numbers, so it is read as the range 0.13-0.23.
6. **`lead_width` = 0.17 / 0.27** — `10X 0.27 / 0.17`, measured across a lead in the top
   view (verified on the render: the arrowheads sit on the two long edges of pin 6).
7. **`land_span` = 4.4** — `(4.4)`, a reference value in parentheses. The render confirms it
   is centre-to-centre: the extension lines drop onto the pad centreline crosses, not onto
   the pad edges.
8. **Pin 2 type** — "Digital output" plus "Open-drain output" maps to `open_collector`, and
   the reference marks that mapping `inferred`. Note the I/O column alone would have said
   `output`.
9. **Pins 3 and 8** — the I/O column prints "Analog", not a direction; mapped to
   `power_in` from the descriptions "Ground" and "Power supply", status `inferred`.
10. **No `group` on any pin.** ADS1115 is a single converter with no separate functional
    units, so the "separate units" condition in the reference is not met.
11. **No `alt_names` anywhere.** The only multi-function pin is 2, whose printed name
    `ALERT/RDY` already carries both functions; "Comparator output or conversion ready" is
    a description, not a second printed name.
12. **`(R0.05) TYP`, `0.25 GAGE PLANE`, `0-8°`, `0.1` coplanarity** appear on p.51-52 but
    have no name in the reference's dimension table, so they were left out rather than
    forced into a wrong name.

## Places the datasheet contradicts itself

**The lead length does not reconcile with the overall width (p.51, DGS0010A).** The top view
is drawn at `SCALE 3.200` and the leads are drawn to that scale: measuring off the 400 dpi
render, the body is 2.9-3.1 mm across and the leads project about 1.0 mm beyond it on each
side, which is what makes the `5.05 TYP / 4.75` tip-to-tip callout add up. But Detail A
dimensions the same lead at `0.7 / 0.4` from toe to body wall. A 2.9-3.1 mm body with
0.4-0.7 mm leads cannot span 4.75-5.05 mm. The two numbers are both printed, so both are
recorded as printed (`lead_length` 0.4/0.7, `overall_width` 4.75/5.05) and the conflict is
flagged here rather than silently resolved. It does not affect the generated footprint, which
is built from the p.52 land pattern.

**Nominal vs. range, minor.** p.1 quotes the package as "3.00mm × 4.90mm" while p.51 gives
2.9-3.1 and 4.75-5.05. These are consistent (3.00 and 4.90 are the mid-points), so only the
p.51 min/max are recorded and no `nom` is added to `overall_width`.
