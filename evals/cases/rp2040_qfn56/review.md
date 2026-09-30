# RP2040 QFN-56 — gold PartSpec review

Datasheet: `rp2040.pdf`, sha256 `be56fbb75ba0ae9e26558a73c93ac3e75c2ad4e6878d3b6703de2a76d886ea8c`,
<https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf>. No revision letter is printed; the
cover page carries `build-date: 2025-02-20`, `build-version: 3184e62-clean`, which is what
`datasheet.revision` records.

All page numbers below are **PDF page indexes** (printed page = PDF page − 1).

Pages that matter:

| PDF page | Printed | What is there |
|---|---|---|
| 12 | 11 | Figure 3, QFN-56 pinout (all 56 pin numbers + names) and Table 1, pin descriptions |
| 608 | 607 | Figure 166, package top/side/bottom views **with a dimension table (see §3)** |
| 609 | 608 | Figure 167, Recommended PCB Footprint — the only land pattern, all in mm |
| 613–615 | 612–614 | §5.5.2 Pin Definitions: Table 614 (pin types), Tables 615–621 (the pin list) |

---

## 1. KiCad disagreements

Symbol: `/usr/share/kicad/symbols/MCU_RaspberryPi.kicad_sym`, symbol `RP2040` (pins live in the
`RP2040_1_1` child, so no `extends` indirection).
Footprint: `/usr/share/kicad/footprints/Package_DFN_QFN.pretty/QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm.kicad_mod`.

The KiCad symbol carries **51** pins; the gold carries **57**. Six physical pins are absent from
KiCad, and four pins get a different name or type.

| # | Pin | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| 1 | 10 `IOVDD` | Table 621: `IOVDD 1, 10, 22, 33, 42, 49` | **absent** from the symbol | Include. Every physical pin gets an entry; the row prints all six numbers. | 615 |
| 2 | 22 `IOVDD` | as above | absent | Include | 615 |
| 3 | 33 `IOVDD` | as above | absent | Include | 615 |
| 4 | 42 `IOVDD` | as above | absent | Include | 615 |
| 5 | 49 `IOVDD` | as above | absent | Include | 615 |
| 6 | 50 `DVDD` | Table 621: `DVDD 23, 50` | **absent** from the symbol | Include | 615 |
| 7 | 52 `QSPI_SCLK` | Table 616 type `Digital IO`; Table 614 defines `Digital IO` = **Bi-directional** | `output` | **bidirectional** (datasheet wins, type is stated on the page) | 614, 613 |
| 8 | 56 `QSPI_SS_N` | Table 616 type `Digital IO` → Bi-directional | `output` (name `~{QSPI_SS}`) | **bidirectional** | 614, 613 |
| 9 | 20 `XIN` | Table 617 type `Analogue (XOSC)`; the **Direction** cell for that type in Table 614 is **empty** | `input` | **passive**, status `inferred` — reference.md: "a pin with no signal direction at all → passive" | 614, 613 |
| 10 | 21 `XOUT` | same type, same empty Direction cell | `output` | **passive**, status `inferred` | 614, 613 |
| 11 | 25 | Table 618 names it **`SWD`**; Figure 3 and Table 1 name it **`SWDIO`** | `SWDIO` | gold uses **`SWDIO`** (the pinout reference, Figure 3, is the primary name list) | 12, 614 |
| 12 | 56 | Table 616 names it **`QSPI_CSn`**; Figure 3 names it **`QSPI_SS_N`** | `~{QSPI_SS}` | gold uses **`QSPI_SS_N`** (Figure 3) | 12, 614 |

Not counted as disagreements (per the task's own carve-out — KiCad merges alternates):

- Pins 38–41: KiCad names them `GPIO26/ADC0` … `GPIO29/ADC3`. Gold uses name `GPIO26` … `GPIO29`
  with `alt_names: ["ADC0"]` … `["ADC3"]`, which is what the skill's `alt_names` rule asks for. The
  primary name agrees. Type `bidirectional` agrees with KiCad (Table 614: `Digital IO / Analogue` =
  "Bi-directional (digital), Standard Digital and ADC input").
- KiCad footprint pad count (57 incl. EP), pitch 0.4, body 7×7, EP 3.2, pad size 0.875 × 0.2 and pad
  centres at ±3.4375 **all agree exactly** with the gold.
- KiCad's four extra 1.29 × 1.29 pads are `F.Paste`-only stencil apertures on the exposed pad, not
  electrical pads. Not a disagreement.

### Footprint cross-check in numbers

| Quantity | Gold (datasheet) | KiCad footprint | Agrees |
|---|---|---|---|
| pads | 56 + EP | 56 + EP | yes |
| pad pitch | 0.40 | 0.4 | yes |
| pad size | 0.875 × 0.20 | 0.875 × 0.2 | yes |
| pad row centre-to-centre | 6.875 | 2 × 3.4375 | yes |
| EP | 3.20 × 3.20 | 3.2 × 3.2 | yes |
| body | 7.0 × 7.0 | 7×7mm | yes |

---

## 2. Values that had to be interpreted

1. **`body_length` = `body_width` = 7.0, status `inferred`.**
   The datasheet never dimensions the package outline in its text layer. 7 mm comes from prose,
   p. 609: *"The RP2040 7×7 mm QFN-56 package is marked as seen in Figure 168"* (also the Figure 3
   caption on p. 12, *"Pinout for QFN-56 7×7mm (reduced ePad size)"*). Interpreting "7×7 mm package"
   as the plastic body size of a leadless QFN is the interpretation, hence `inferred`.

2. **`pitch` = 0.40, from the land pattern.** Figure 167 (p. 609) dimensions the **pad** pitch 0.40;
   on the rendered page the arrows bracket two adjacent pad centres of the bottom row. The package
   outline's own `e 0.400 BSC` (Figure 166, p. 608) agrees but is not quotable — see §3.
   Status `extracted`.

3. **`land_span` = 6.875, status `inferred`.** Figure 167 prints **6.00** between the *inner* edges of
   opposite pad columns (and between the inner edges of the top and bottom pad rows), and **0.875**
   for the radial length of one pad. Centre-to-centre = 6.00 + 0.875 = **6.875**, which is what
   `land_span` is defined to be and what the generator places pads at (±3.4375). Cross-checked
   against the KiCad footprint, whose pad centres are at x = ±3.4375.
   Cross-check on the rendered figure: outer copper edge to outer copper edge = 0.875 + 6.00 + 0.875
   = **7.75**, exactly the figure's outermost dimension, so the three readings are self-consistent.

4. **`land_pad_length` = 0.875 / `land_pad_width` = 0.20.** Figure 167 callouts. On the rendered page
   the `0.20` arrows bracket one pad's extent along the pad row (33 px at 600 dpi ≈ 0.22 mm, stroke
   included) and the `0.875` callout's extension lines bracket the bottom pad row's top and bottom
   edges (131 px ≈ 0.88 mm). The pads are 0.875 long radially and 0.20 wide tangentially, so the
   0.40 pitch leaves a 0.20 mm gap — unusually tight, which is the point of the note on p. 608
   ("standard 0.4mm QFN-56 footprints provided with CAD tools may need adjusting").
   Both `extracted`.

5. **`land_ep_size` = 3.20.** Figure 167's `3.20` on both axes, drawn around the central pad
   (477 × 476 px ≈ 3.20 × 3.20). `extracted`.

6. **Name splits on pins 38–41** — `GPIO26` + `alt_names ["ADC0"]` etc., per the skill's rule that
   extra *functions* go in `alt_names`. Table 615 prints `GPIO26 / ADC0`.

7. **Exposed pad named `GND`, not `EP`.** Table 621 gives the central pad number **57** and name
   **GND** ("Common ground connection via central pad"), and Figure 3 labels the centre `GND`. The
   skill's "an exposed pad is named `EP`" applies when the datasheet prints no name; here it does,
   and KiCad also uses `GND`. Type `power_in` (ground), status `inferred` — so the pin's *number and
   name are extracted but its type is derived*, and the field can only carry one status.

8. **`XIN`/`XOUT` = `passive`.** Table 614 (p. 613) has a `Direction` column; the cell for
   `Analogue (XOSC)` is **blank**, so the datasheet prints no direction for either pin. The
   description cell does say "Oscillator input pins", but that sentence covers both XIN and XOUT,
   and XOUT is physically an output — it cannot be taken as a per-pin direction. reference.md sends
   "a pin with no signal direction at all" to `passive` with status `inferred`. Both pins `inferred`.

9. **No `group` on any pin.** The part has no separate units (no analogue/digital amplifier blocks to
   label A/B). Supply pins are therefore left ungrouped rather than given a `"power"` group.

10. **`QSPI_SS_N` / `SWDIO` spelling.** Taken from Figure 3 (p. 12), the pinout reference, where each
    pin gets exactly one name. The pin-definition tables spell them `QSPI_CSn` and `SWD`. The
    `source.quote` for these two pins is therefore the table row (which carries the number and the
    type) and the *name* comes from the figure; the number↔name pairing was checked on the rendered
    Figure 3.

11. **`7.75` and `1.175` from Figure 167 are recorded nowhere.** `7.75` is the overall copper span
    (outer edge to outer edge, both axes) and `1.175` is the step from the bottom of a side pad
    column to the bottom of the bottom pad row. PartSpec has no dimension name for either, and
    inventing one would be worse than leaving it out. Both are recoverable from the gold:
    `7.75 = land_span + 2 × land_pad_length = 6.875 + 1.75`.

12. **No `height`, `standoff`, `ep_size`, `lead_width`, `lead_length`.** The datasheet *does* print
    them — but only inside Figure 166, whose drawing is converted to vector outlines: the page has
    **no text layer at all** for the figure (`pdftotext -f 608 -l 608` returns the section headings
    only; `pdffonts`/`pdfimages` list no image and no font used by the drawing; the string `BSC` does
    not occur anywhere in the file's content streams). A PartSpec value must carry a verbatim quote
    that the validator can find on the cited page, so these cannot be recorded. **A human adding them
    by hand from the rendered page would get, all in mm:**

    | Symbol | Meaning | Min | Nom | Max |
    |---|---|---|---|---|
    | A | overall package height | | 0.900 | |
    | A1 | standoff | 0.000 | | 0.050 |
    | A2 | (terminal plane / upper datum) | | 0.650 | 0.700 |
    | A3 | REF | | 0.203 REF | |
    | b | terminal width | 0.130 | 0.180 | 0.230 |
    | D | body length | | 7 BSC | |
    | D2 | ePad, X | 3.00 | 3.100 | 3.200 |
    | E | body width | | 7 BSC | |
    | E2 | ePad, Y | 3.00 | 3.100 | 3.200 |
    | L | terminal length | 0.300 | 0.400 | 0.500 |
    | e | pitch | | 0.400 BSC | |
    | R | corner radius | 0.065 | | |

    Geometrical tolerances printed below the table: aaa 0.100, bbb 0.070, ccc 0.100, ddd 0.050,
    eee 0.080, fff 0.100. These would become `height` (nom 0.9), `standoff` (0.0–0.05),
    `ep_size` (3.0–3.2, nom 3.1), `lead_width` (0.13–0.23, nom 0.18) and `lead_length`
    (0.3–0.5, nom 0.4) — all on PDF page 608. They do not affect the generated symbol or footprint.

---

## 3. Where the datasheet contradicts itself

1. **Pin 25 is `SWD` or `SWDIO`.** Table 618 (p. 614) prints `SWD`; Figure 3 (p. 12) and Table 1
   (p. 12) print `SWDIO`. Gold uses `SWDIO`.

2. **Pin 56 is `QSPI_CSn`, `QSPI_SS_N` or `QSPI_SS`.** Table 616 (p. 614) prints `QSPI_CSn`, Figure 3
   (p. 12) prints `QSPI_SS_N`, and the body text on p. 237 (§4.10, XIP) prints `QSPI_SS`. Gold uses
   `QSPI_SS_N`.

3. **The land pattern's callouts are easy to bind to the wrong feature.** In Figure 167 the `0.875`
   and `1.175` dimensions sit under the bottom pad row, but both are *vertical* dimensions whose
   extension lines point at horizontal edges — `0.875` at the bottom row's top and bottom edges
   (i.e. one pad's radial length) and `1.175` at the side column's last pad and the bottom row's
   bottom edge. Read at 150 dpi they look like they measure the gaps at the corners. The values
   recorded here come from pixel measurement at 600 dpi of the extension-line endpoints, cross-checked
   against KiCad's pad size, and they close exactly: `0.875 + 6.00 + 0.875 = 7.75`.

4. **`1.175` is not the complement of `0.875`.** `7.75 − 6.00 = 1.75` splits symmetrically into
   `0.875 + 0.875` — the top and bottom pad rows, which is what the 6.00 vertical dimension spans
   (inner edge to inner edge). `1.175` measures something else: from the bottom of a side pad column
   to the bottom of the bottom pad row, i.e. `0.875` (the bottom row's radial length) plus the
   `0.30` gap that opens up because the side columns are inset relative to the top and bottom rows
   (41 px ≈ 0.28 mm at 600 dpi). The two values are therefore not in conflict — a reader who
   assumes they are complementary will be off by 0.30 mm. `1.175` is not recorded (no PartSpec
   dimension name); nothing in the gold depends on it.

Nothing else in the datasheet contradicts itself on this package. Pin 50 in particular is **not**
contradictory: Figure 3 and Table 621 agree that it is `DVDD`.

---

## 4. Verification done

- Every one of the 57 pins was read from the text of the pin tables (PDF pp. 613–615) **and** its
  number↔name pairing was confirmed on the rendered image of Figure 3 (p. 12, rendered at 150 and
  400 dpi and cropped into four overlapping views covering the top row, left column, right column and
  bottom row). All 56 perimeter pins matched.
- Every dimension was read from the text of Figure 167 (p. 609) and confirmed against the rendered
  image at 150 and 600 dpi; the geometry was measured from the pixels to make sure each number is
  attached to the feature it labels.
- `kicad-partspec validate spec.gold.json --datasheet rp2040.pdf` → `passed: true`
  (18 warnings, all of kind `status.inferred`: 15 pins + 3 dimensions).
- `kicad-partspec build spec.gold.json --out out --concise` → `passed: true`, 0 failures; emits
  `out/RP2040.kicad_sym` (57 pins) and
  `out/partspec.pretty/QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm.kicad_mod` (57 pads).