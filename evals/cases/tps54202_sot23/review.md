# TPS54202 (DDC, SOT-23-6) — gold PartSpec review

Datasheet: `tps54202.pdf`, sha256 `8bace250…6373b`, SLVSD26C (Rev. C, February 2026).
Pages cited in the spec are PDF page indexes (the datasheet's printed page number equals the PDF index
for pages 1–23; the mechanical pages 28–30 have no printed number).

`kicad-partspec validate` passes; `kicad-partspec build --concise` passes with 0 failures.

## 1. KiCad cross-check

### 1.1 Symbol

**The library installed here has no `TPS54202DDC`.** `/usr/share/kicad/symbols/Regulator_Switching.kicad_sym`
contains `TPS54302` and no `TPS54202*` entry, so the cross-check was made against `TPS54302`, whose
pinout is identical to the TPS54202 DDC (VIN 3, EN 5, GND 1, BOOT 6, SW 2, FB 4 — same numbers and names
as Table 4-1 of this datasheet). No `extends` is involved: `TPS54302` holds its own pins.

| Pin | Datasheet says (p. 3, Table 4-1 / Figure 4-1) | Gold | KiCad `TPS54302` | Disagreement | Decision |
|---|---|---|---|---|---|
| 1 | `GND`, TYPE `–`, "Ground pin. Source terminal of low-side power NFET…" | `power_in` (inferred) | `power_in` | no | — |
| 2 | `SW`, TYPE `O`, "Switch node connection between high-side NFET and low-side NFET" | `output` (extracted) | `power_out` | **yes — type** | Datasheet wins (p. 3 prints `O`, and the skill's first mapping row is "output (O) → `output`"). See note A. |
| 3 | `VIN`, TYPE `–`, "Input voltage supply pin…" | `power_in` (inferred) | `power_in` | no | — |
| 4 | `FB`, TYPE `I`, "Converter feedback input…" | `input` (extracted) | `input` | no | — |
| 5 | `EN`, TYPE `I`, "This pin is the enable pin. Float the EN pin to enable." | `input` (extracted) | `input` | no | — |
| 6 | `BOOT`, TYPE `O`, "Supply input for the high-side NFET gate drive circuit." | `output` (extracted) | `passive` | **yes — type** | Datasheet wins (p. 3 prints `O`; `passive` is reserved for pins with no printed direction). See note B. |

Pin **numbers and names**: 6/6 agree with both Table 4-1 and the Figure 4-1 top view (rendered p. 3:
left column 1 GND, 2 SW, 3 VIN; right column 6 BOOT, 5 EN, 4 FB), and 6/6 agree with KiCad.

**Note A — `SW`.** KiCad's `power_out` is defensible engineering (SW is a power node), and the
PartSpec rules do have a "a supply the part produces → `power_out`" row. But SW is not a supply of the
chip, it is the switching node, and the datasheet prints an explicit direction for it (`O`). Following
the printed direction keeps SW and BOOT on one single rule. If a reviewer prefers KiCad's convention,
both pins would become `power_out` and nothing else in the spec would change.

**Note B — `BOOT`.** The description calls it a supply, so `power_out` (inferred) is the other
defensible reading. The printed `O` was taken as the direction; `passive` (KiCad) would be wrong under
the skill, which reserves `passive` for pins with no signal direction at all.

`GND` and `VIN` are the only pins marked `inferred`: their TYPE column is `–`, so the type comes from
the supply/ground rows of the type table.

### 1.2 Footprint — `Package_TO_SOT_SMD.pretty/SOT-23-6.kicad_mod`

6 pads; pad 1/2/3 at x = −1.1375 (y = −0.95, 0, +0.95), pad 4/5/6 at x = +1.1375 (y = +0.95, 0, −0.95);
pad size 1.325 × 0.6, roundrect rratio 0.25; F.Fab body 1.6 × 2.9. Note pins 1 and 4 are diagonally
opposite, which matches the datasheet pinout (1 and 4 on opposite corners).

| Dimension | Datasheet | Gold | KiCad | Disagreement | Decision |
|---|---|---|---|---|---|
| pad count | 6 pins (p. 3) | 6 | 6 | no | — |
| pitch | `4X 0.95` (p. 28, top view) | 0.95 | 0.95 (pad y spacing) | no | — |
| body length | 3.05 / 2.75 (p. 28) | 2.75–3.05 | 2.9 (F.Fab) | no (nominal agrees) | — |
| body width | 1.75 / 1.45 (p. 28) | 1.45–1.75 | 1.6 (F.Fab) | no (nominal agrees) | — |
| overall width | 3.05 / 2.55 (p. 28) | 2.55–3.05 | copper to ±1.80 | not comparable | KiCad's outer copper edge is a land-pattern value, not the package tip-to-tip; expected to be larger. |
| `land_pad_length` | `6X (1.1)` (p. 29) | 1.1 | 1.325 | **yes — but not resolvable** | KiCad pads come from IPC-7351, so pad size legitimately differs. Datasheet wins (the rule is that `land_*` comes only from the example land pattern). |
| `land_pad_width` | `6X (0.6)` (p. 29) | 0.6 | 0.6 | no | — |
| `land_span` | `(2.7)` (p. 29) | 2.7 | 2.275 (pad centres ±1.1375) | **yes — but not resolvable** | Same IPC-vs-datasheet situation: the datasheet's land pattern is wider than the IPC-7351 nominal. Datasheet wins. |

Both real dimension differences (pad length, row spacing) are exactly the category the task allows to
differ. Pitch, body size and pad width agree.

## 2. Values that had to be interpreted

1. **Which of the two `3.05 / xx` pairs is what (p. 28 top view).** The drawing prints `3.05/2.55`
   horizontally and `3.05/2.75` vertically. On the rendered page the horizontal pair's extension lines
   land on the *lead tips* (x ≈ 330 and 635 px) and the vertical pair's on the *body* edges
   (y ≈ 390 and 720 px), so the horizontal one is tip-to-tip across the two lead rows
   (`overall_width` = 2.55–3.05) and the vertical one is the body along the pin rows
   (`body_length` = 2.75–3.05). This also agrees with page 1's "2.9mm × 2.8mm (length × width
   including pins)": 2.9 = body length nominal, 2.8 = the midpoint of 2.55–3.05.
2. **`1.75 / 1.45` (p. 28 top view)** = the body across the two lead rows, i.e. `body_width`
   (1.45–1.75). Its extension lines span only the body rectangle.
3. **`1.1 / 0.7` (p. 28, upper-right view) = `height`, 0.7–1.1.** This was the least obvious call on the
   page. Three pieces of evidence: (a) the drawing title says "SOT-23 – 1.1 **max height**"; (b) the
   only other horizontal extent in that view is the body silhouette, and the body width is already
   1.45–1.75 in the top view; (c) a pixel measurement — the body measures 815 px along this view's
   vertical axis and 250 px horizontally, and the three lead tabs in the view sit 0.95 mm apart, giving
   a scale of ≈281 px/mm; 815 px → 2.86 mm (the 2.9 mm body length) and 250 px → 0.89 mm, the midpoint
   of 0.7/1.1. The `0.1 / 0.0 TYP` callout beside it measures 25 px = 0.09 mm at the same scale,
   confirming the scale. Marked `extracted`; the number and its meaning are both printed on p. 28.
4. **`0.6 / 0.3 TYP` vs `6X 0.5 / 0.3` (p. 28).** Two different callouts that share the value 0.3.
   The `6X 0.5/0.3` sits in the **top view** next to a lead, across the lead → `lead_width`
   (0.3–0.5). The `0.6/0.3 TYP` sits in the **profile view**, measuring horizontally from the lead tip
   to the tangent where the lead starts to rise → `lead_length` (foot length, 0.3–0.6).
5. **`0.20 / 0.12 TYP` (p. 28, profile view) = `standoff`, 0.12–0.20.** The arrows run vertically from
   the seating plane (the lower line, which the "SEATING PLANE" leader points at) to the underside of
   the lead foot. Note the drawing calls this the lead-to-seating-plane gap, not a body-to-seating-plane
   gap; `standoff` is the same JEDEC quantity (S).
6. **Stacked pairs read as max over min.** The drawing prints limits top/bottom
   (3.05/2.55, 1.75/1.45, 3.05/2.75, 1.1/0.7, 0.5/0.3, 0.6/0.3, 0.20/0.12), which is TI's convention
   throughout, so each became `min`/`max`. The two pairs that carry `TYP` (0.6/0.3 and 0.20/0.12) were
   recorded as `min`/`max` rather than a single `nom`, because two numbers are printed and the pair
   still bounds the value.
7. **Land pattern orientation (p. 29).** The pads are drawn as horizontal rectangles: the `6X (1.1)`
   dimension is horizontal, i.e. along the lead direction, so `land_pad_length` = 1.1; the `6X (0.6)`
   dimension is vertical, i.e. across, so `land_pad_width` = 0.6.
8. **`(2.7)` = `land_span`, marked `inferred`.** On the rendered page the dimension runs between the
   vertical centre lines of the two pad rows, so it is a centre-to-centre row spacing. The *meaning* is
   an interpretation of an unlabelled number, hence `inferred` (the same call the `lm358_soic8` gold
   makes for its `land_span`).
9. **The `1.9` callout (p. 28) was left out.** It spans pin 1 to pin 3 centres and is exactly 2 ×
   0.95; the PartSpec dimension vocabulary has no name for a lead-row span (`land_span` is land-pattern
   only), so it is not recorded.
10. **Left out because the vocabulary has no name:** `(R0.05) TYP` pad corner radius, the `0 -8 TYP`
    lead-foot angle, `4X 4 -15` body draft, `4X 0 -15` lead angle, the `0.2(M) C A B` position
    tolerance, `0.25 GAGE PLANE`, the `0.1 / 0.0 TYP` lead-tip offset, and the `0.07 MAX/MIN ARROUND`
    solder-mask values on p. 29. No `body_thickness`, `lead_thickness` or `ep_size` is given at all
    (SOT-23-6 DDC has no exposed pad and no separate body-height callout).
11. **`package.family` = `"SOT"`.** The datasheet calls the package "SOT-23 (6)", "SOT-23-THIN (DDC)",
    "DDC (SOT-23, 6)" and the drawing titles it "SOT-23 — SMALL OUTLINE TRANSISTOR"; it never says
    "SOP" or "SOIC". Consequence: `kicad-partspec build` reports
    `footprint.skipped — package family 'SOT' is not supported (supported: dual-row and quad
    packages)`, because the generator's dual-row list is {SOIC, SOP, SSOP, TSSOP, MSOP, VSSOP}. The
    land-pattern dimensions are all extracted anyway. Writing `"SOP"` instead would generate
    `SOP-6_1.6x2.9mm_P0.95mm.kicad_mod`, but that is a family name the datasheet does not use, so the
    spec keeps `"SOT"`. Flagged for the eval author: **the installed tool cannot emit a footprint for a
    SOT-23.**
12. **`mpn` = `"TPS54202"`** (the device name, matching the `lm358_soic8` gold convention of no package
    suffix). The orderable parts are `TPS54202DDCR` / `TPS54202DDCT` (p. 24); the KiCad symbol this
    datasheet is paired with is `TPS54202DDC`.
13. **`status: inferred`** on pins 1 and 3 only (`power_in` chosen through the supply/ground rows of the
    type table) and on `land_span`.

## 3. Datasheet self-contradictions

- **Thermal shutdown threshold: 160 °C vs 155 °C.** Table 5-5 (p. 5) gives "Thermal Shutdown, rising
  temperature 160 °C", and the Revision History (p. 22) lists "Changed the typical thermal shutdown
  rising temperature from 155 °C to 160 °C in the Electrical Characteristics table". But §6.3.14
  Thermal Shutdown (p. 12) still reads "if the junction temperature exceeds **155 °C** typically. When
  the junction temperature drops below **145 °C** typically…". §6.3.14 was not updated with the rest of
  Rev. C. Nothing in the PartSpec depends on it.
- Not a contradiction, but noted so it is not mistaken for one: the shutdown current reads 3 µA in the
  Features, in Table 5-5 and in §6.1 (the Rev. C change from 2 µA was applied in all three places), and
  "5mS"/"5ms" soft start is just inconsistent unit capitalisation between the Features list and the
  Description.

No mechanical contradiction was found: page 1's "2.9mm × 2.8mm" package size, the p. 28 outline, and
JEDEC MO-193 are mutually consistent, and Figure 4-1, the page-1 simplified schematic and Table 4-1
agree on all six pin numbers and names.
