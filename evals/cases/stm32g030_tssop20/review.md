# Review: ST STM32G030F6P6, TSSOP20

Datasheet `stm32g030.pdf`, SHA-256 `b86b1fa79171e8ed521745305bff03d43d75f07729c077e0c4e7badc896711d3`,
document **DS12991 Rev 6** (20-Jun-2025). Printed page numbers equal PDF page indexes throughout
(verified: the pinout figure is on both page 29, Table 70 on page 86, Figure 32 on page 87).

Sources used:

- page 29 — Figure 4, STM32G030Fx TSSOP20 pinout (binds pin number to name)
- pages 31–34 — Table 12, Pin assignment and description (pin type / I/O structure)
- page 86 — Figure 31 TSSOP20 Outline + Table 70 TSSOP20 Mechanical data
- page 87 — Figure 32 TSSOP20 Footprint example

Every one of the 20 pins and all 13 dimensions was checked on the rendered page image
(`pdftoppm -r 150/200/300/600`), not only in the text layer.

## 1. KiCad disagreements

KiCad symbol `STM32G030F6Px` (`MCU_ST_STM32G0.kicad_sym`) has 20 pins, matching the datasheet's 20
physical pins. KiCad footprint `TSSOP-20_4.4x6.5mm_P0.65mm` has 20 pads.

### Pins

| # | Item | Datasheet | KiCad | Decision | Page |
|---|---|---|---|---|---|
| P1 | Pin 1 name form | `PB7/PB8` (two port names on one pad) | merged `PB7/PB8` | Not a real disagreement — KiCad merges bonded names. Gold splits them: `name: PB7`, `alt_names: [PB8]`. | 29 |
| P2 | Pin 2 name form | `PB9/PC14-OSC32_IN` | merged `PB9/PC14` | Datasheet wins; gold `name: PB9`, `alt_names: [PC14-OSC32_IN]`. KiCad drops the `-OSC32_IN` suffix. KiCad's port-alternate set for pin 2 is {PB9, PC14}, identical to gold's pair. | 29 |
| P3 | Pin 3 name | `PC15-OSC32_OUT` | `PC15` | **Datasheet wins.** Figure 4 prints `PC15-OSC32_OUT`; Table 12 names it `PC15-OSC32_OUT (PC15)`. KiCad abbreviates the pin to the bare port name and carries `RCC_OSC32_OUT` as an alternate function instead. Gold uses the printed name. | 29, 31 |
| P4 | Pin 4 name | `VDD/VDDA` | `VDD` | **Datasheet wins** (abbreviation, not a different pin). | 29 |
| P5 | Pin 5 name | `VSS/VSSA` | `VSS` | **Datasheet wins** (abbreviation). | 29 |
| P6 | Pin 6 electrical type | Table 12 "Pin type (function upon reset)" = **I/O**, I/O structure `RST` | `input` | **Datasheet wins.** The pin type column prints `I/O`, and reference.md maps I/O to `bidirectional`. Gold: `bidirectional`, `status: extracted`. Precedent: the existing `atmega328p_tqfp32` gold types the RESET pin `PC6` as `bidirectional` for the same reason. | 31 |
| P7 | Pin 15 primary name order | `PB0/PB1/PB2/PA8` | `PA8/PB0/PB1/PB2` | **Datasheet wins on order only.** The set of bonded ports {PB0, PB1, PB2, PA8} is identical in both. Gold `name: PB0`, `alt_names: [PB1, PB2, PA8]`. | 29 |
| P8 | Pin 16 primary name | `PA11[PA9]` | `PA9/PA11` | **Datasheet wins on order.** Set {PA9, PA11} identical. `PA11` is the default mapping (Table 12 note 4). Gold `name: PA11`, `alt_names: [PA9]`. | 29, 33 |
| P9 | Pin 17 primary name | `PA12[PA10]` | `PA10/PA12` | **Datasheet wins on order.** Set {PA10, PA12} identical. Gold `name: PA12`, `alt_names: [PA10]`. | 29, 33 |
| P10 | Pin 19 primary name | `PA15/PA14-BOOT0` | `PA14/PA15` | **Datasheet wins on order.** Set {PA14, PA15} identical. Gold `name: PA15`, `alt_names: [PA14-BOOT0]`. | 29, 33 |
| P11 | Pin 20 primary name order | `PB3/PB4/PB5/PB6` | `PB3/PB4/PB5/PB6` | Agree. | 29 |

No disagreement on: pin count (20), pin **numbers** (1–20 all identical to KiCad), which port names are
bonded to which pin, GPIO electrical type (`bidirectional`), or the supply pins' `power_in`.

### Dimensions / footprint

| # | Item | Datasheet | KiCad | Decision | Page |
|---|---|---|---|---|---|
| D1 | Body size | D 6.500 typ × E1 4.400 typ | F.Fab body 6.5 × 4.4 (±3.25, ±2.2) | Agree. | 86 |
| D2 | Pitch | e = 0.650 | 0.65 (pad y step) | Agree. | 86 |
| D3 | Land pad width | 0.40 | 0.40 | Agree. | 87 |
| D4 | Land pad length | 1.35 | 1.475 | **Datasheet wins.** KiCad pads are generated from IPC-7351 / JEDEC MO-153 (see the footprint's `descr` field), ST publishes its own recommended land pattern on page 87. A legitimate difference; pad length does not affect the fab body either way. | 87 |
| D5 | Land row centre-to-centre span | 5.75 (derived from ST's 4.40 inner-edge gap + 1.35 pad length) | 5.725 (pads at x = ±2.8625) | **Datasheet wins.** The two agree to 0.025 mm, which independently confirms the derivation. | 87 |

KiCad footprint pad count (20), pitch (0.65) and body size (4.4 × 6.5) agree with the datasheet.

## 2. Interpretations

1. **`land_span` = 5.75 mm — derived, not printed.** Page 87 prints two vertical dimensions of the
   land pattern: `7.10` (outer edge of one pad row to outer edge of the other) and `4.40` (inner edge
   to inner edge). Neither is the centre-to-centre row span that `reference.md` defines as
   `land_span`. The drawing is internally consistent — 4.40 + 2 × 1.35 = 7.10 — so the centre-to-centre
   span is 4.40 + 1.35 = **5.75 mm**. Recorded with `status: inferred`; `land_span` is `REQUIRED` for
   footprint generation, so omitting it would have skipped the footprint entirely. Cross-checked against
   KiCad's independently-generated 5.725 mm.
2. **Primary pin name = the first name printed in Figure 4 (page 29).** Figure 4 is the page that binds
   number to name, and it is the only TSSOP20 pinout listing in the datasheet. Applied uniformly this
   gives PB7 / PB9 / PC15-OSC32_OUT / VDD/VDDA / VSS/VSSA / NRST / PA0…PA7 / PB0 / PA11 / PA12 /
   PA13 / PA15 / PB3. It differs from KiCad's ordering on pins 15, 16, 17 and 19 (see the table above),
   where KiCad appears to order by its own convention (the remappable/reversed GPIO first).
3. **`alt_names` = the other port names printed on the same pin in Figure 4, and nothing else.**
   Table 12's "Alternate functions" and "Additional functions" columns (`ADC_IN4`, `USART1_TX`,
   `TIM1_CH4`, `WKUP2`, …) are peripheral-function names, not the port names the pad is bonded to; they
   were deliberately left out. This matches how the existing `atmega328p_tqfp32` gold records
   port-level alternates (`PCINT6`, `XTAL1`) and not every peripheral function.
4. **NRST typed `bidirectional`, not `input`.** Table 12's "Pin type (function upon reset)" column
   prints `I/O` for NRST; `reference.md` maps I/O to `bidirectional`. KiCad's `input` is the outlier.
5. **Outline symbol letter → PartSpec dimension name.** ST's Table 70 gives only bare letters, so every
   one of A, A1, A2, b, c, D, E, E1, L required reading Figure 31 to know what it measures. All are
   marked `status: inferred` per reference.md ("mark that dimension `inferred`"). Mapping used, each
   confirmed against the rendered drawing:
   `A`→height, `A1`→standoff, `A2`→body_thickness, `b`→lead_width, `c`→lead_thickness,
   `D`→body_length, `E`→overall_width, `E1`→body_width, `L`→lead_length, `e`→pitch.
   `pitch` alone is `extracted`, because page 86's prose spells it out:
   "6.5 x 4.4 mm thin small-outline package with 0.65 mm pitch".
6. **`land_pad_length` (1.35) vs `land_pad_width` (0.40).** Both are bare numbers in Figure 32; the
   drawing shows the pads as vertical rectangles 1.35 tall (along the lead direction) and 0.40 wide.
   Both marked `inferred`.
7. **Omitted dimensions.**
   - `L1` (typ 1.000 mm): measured in Figure 31 from the lead's shoulder to the toe, i.e. longer than the
     lead foot `L`. No PartSpec dimension name covers it and it is not a body or land dimension, so it
     was left out rather than mislabelled.
   - `k` (0°–8°, foot angle) and `aaa` (0.100, general tolerance): angular/tolerance terms, not
     dimensions.
   - `C`: drawn on Figure 31 as a second callout for overall height but has no row in Table 70; `A`
     (max 1.200) covers it.
   - No `overall_length`: in TSSOP the leads end flush with the body ends, so `D` is the only
     along-the-row length the drawing gives. There is no lead-tip-to-lead-tip length to record.
   - The pad-to-pad gap of 0.25 mm printed twice in Figure 32 is redundant with pitch 0.65 minus pad
     width 0.40 and has no PartSpec name; not recorded.

## 3. Places where the datasheet contradicts itself

1. **Package size on the cover vs in Section 6.3.** Page 1 lists TSSOP20 as "**6.4 × 4.4 mm**" and
   pages 88–90 repeat "TSSOP20 6.4 × 4.4 mm" in the thermal tables. Page 86 says "TSSOP20 is a 20-lead,
   **6.5** x 4.4 mm thin small-outline package" and Table 70 gives D typ = 6.500 (body length) and
   E typ = 6.400 (lead-tip-to-lead-tip overall span). The cover is quoting `E`, not `D`; the body is
   6.5 mm. Gold follows the mechanical table: `body_length` 6.4/6.5/6.6, `overall_width` 6.2/6.4/6.6.
   KiCad's footprint name and F.Fab body (4.4 × 6.5) agree with the table, not the cover.
2. **Two symbols for overall height.** Figure 31 labels the overall height `A` in the front view and
   `C` in the side view, but Table 70 tabulates only `A`. Gold uses `A` (max 1.200 mm).
3. **"Drawing is not to scale"** (note 1 under Figure 31) — the proportions in the drawing cannot be
   used to sanity-check the table; only the callout labels were used.
4. No contradiction was found between Figure 4 (page 29) and Table 12 (pages 31–34). All 20 TSSOP20
   pin numbers were cross-checked in both, and the two agree exactly — including the non-obvious
   bonds at pins 1/2 (PB9 is on pin **2**, not pin 1), 15 and 19.