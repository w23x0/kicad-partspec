# CP2102N-A02-GQFN24 — gold key review

Datasheet: `cp2102n.pdf`, sha256 `32fbab0ba17f394ab76fbbd8129bddad228c1c486a1693d96ea5905936e437fe`, **Rev. 1.5 (November 2020)**.
Printed page numbers equal PDF page indexes throughout (cover is page 1), so every page cited below is the PDF index.

Pages used:

| Page | What is on it |
|---|---|
| 2 | Table 1.1 Product Selection Guide (`CP2102N-A02-GQFN24`, QFN24) |
| 19 | Table 4.2 GPIO Pin Alternate Functions (QFN24 column), and the note that CLK shares the RI pin |
| 29 | Figure 5.2 CP2102N QFN24 Pinout; Table 5.2 rows 1–3 |
| 30 | Table 5.2 rows 4–24 and the unnumbered `Center` row |
| 37 | Figure 7.1 QFN24 Package Drawing; Table 7.1 Package Dimensions |
| 39 | Figure 7.2 PCB Land Pattern; Table 7.2 Land Pattern Dimensions |
| 46 | Section 10 Revision History (Rev. 1.5 = November 2020) |

## 1. KiCad disagreements

KiCad sources: symbol `CP2102N-Axx-xQFN24` in `/usr/share/kicad/symbols/Interface_USB.kicad_sym` (25 pins, does not
`extends` a parent), footprint `QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm.kicad_mod`.

Pin numbering, pad count (25 = 24 + EP), pitch (0.5), row spacing and body size all agree. The disagreements:

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| 1 | Pin 25 (exposed pad) electrical type | Table 5.2 row `Center`: `GND` — `Ground` | `passive` (hidden pin, same position as pin 2 GND) | **Gold: `power_in`, `inferred`.** The skill's pin-type table says an exposed pad tied to ground is `power_in`, and the datasheet calls the pad Ground. KiCad's `passive` is a duplicate-of-GND modelling choice, not a claim about direction. | 30 |
| 2 | Pin 25 name | `Center` row, name `GND` | name `GND` | **Gold: `EP`.** The datasheet prints no pin number and no net name for the pad position; the skill requires an exposed pad to be named `EP` with no `alt_names`. | 30 |
| 3 | Pins 11–14 name order | `GPIO.3 / WAKEUP`, `GPIO.2 / RS485`, `GPIO.1 / RXT`, `GPIO.0 / TXT` (Table 5.2 and Figure 5.2) | `~{WAKEUP}/GPIO.3`, `RS485/GPIO.2`, `~{RXT}/GPIO.1`, `~{TXT}/GPIO.0` | **Gold: datasheet order** — name `GPIO.3`/`GPIO.2`/`GPIO.1`/`GPIO.0`, `alt_names` `WAKEUP`/`RS485`/`RXT`/`TXT`. KiCad inverts the order; the datasheet prints GPIO first. | 30 |
| 4 | Pin 1 name | `RI / CLK` | `~{RI}/CLK` | No disagreement on content. Gold name `RI`, `alt_names` `["CLK"]`, per the skill's `alt_names` rule. | 29 |
| 5 | Pin 15 name | `SUSPENDb` (active low) | `~{SUSPEND}` (overbar) | No disagreement on content; KiCad uses an overbar where the datasheet uses the `b` suffix. Gold keeps the datasheet spelling. | 30 |
| 6 | Pins 18, 19, 22, 23, 24 names | `CTS`, `RTS`, `DSR`, `DTR`, `DCD`, all described "(active low)" | `~{CTS}`, `~{RTS}`, `~{DSR}`, `~{DTR}`, `~{DCD}` | Not a disagreement: the datasheet gives no base name with a bar, only prose. Gold keeps the printed names. | 30 |
| 7 | Land pad size | X1 = 0.30, Y1 = 0.85 (Table 7.2) | pad `0.825 x 0.25` | **Gold: 0.30 / 0.85.** KiCad's pads are IPC-7351 nominal; the datasheet's own land pattern wins. | 39 |
| 8 | Land exposed-pad size | X2 = Y2 = 2.55 (Table 7.2) | EP pad `2.6 x 2.6` | **Gold: 2.55.** Same reason — IPC vs. the manufacturer's land pattern. | 39 |
| 9 | Land row-to-row span | C1 = C2 = 3.90 (Table 7.2) | pad centres at ±1.9375 → span 3.875 | **Gold: 3.90.** Same reason; the 25 µm difference is IPC rounding. | 39 |
| 10 | Pin 6 `VDD` type | `Supply Power Input / 5V Regulator Output` | `power_in` | Agreement. Gold `power_in`, `inferred`. | 30 |
| 11 | Pins 3, 4 `D+` / `D-` type | `USB Data Positive` / `USB Data Negative` — no direction printed | `bidirectional` | Gold `bidirectional`, `inferred`, following the KiCad hint for a signal whose direction the datasheet does not state. | 29, 30 |
| 12 | Pin 9 `RSTb` type | `Active-low Reset` — no direction printed | `input` | Gold `input`, `inferred`. | 30 |

Everything else agrees pin for pin: 1 bidirectional, 2 `power_in`, 5/6/7 `power_in`, 8 `input`, 10/16 `no_connect`,
11–14 `bidirectional`, 15/17/19/21/23 `output`, 18/20/22/24 `input`. KiCad hides pins 10 and 16 (no-connect) and pin 25;
the gold does not model visibility.

## 2. Values that had to be interpreted

- **`land_span` = C1 = C2 = 3.90.** Table 7.2 does not say what C1/C2 measure. On the rendered page 39 drawing the C1
  extension lines fall on the centrelines of the left and right pad columns (not their outer edges), i.e. it is a
  centre-to-centre row span, which is what `land_span` means. Two cross-checks agree: the drawn scale from the 0.5 mm
  pitch puts the C1 span at ~4.0 mm (a centre-to-centre span of 3.90 + 0.15 pad = 4.05 outer, and an outer-edge span
  would have to be 4.75 mm, which the drawing plainly is not), and KiCad's IPC land pattern independently puts the same
  span at 3.875. Marked `inferred`.
- **`land_ep_size` = X2 = Y2 = 2.55.** Also ambiguous. On the rendered drawing the X2 extension lines coincide with the
  drawn edges of the centre pad, and the drawn span between them measures 2.55 mm at the drawing's own scale. The rival
  reading — the span from pad 1 to pad 6 centreline — would be 5E = 2.50, which the tabulated 2.55 does not match. The
  drawn EP outline itself is slightly loose (~2.65 mm at drawing scale), but X2's own arrows measure 2.55. Cross-check:
  the package EP max is 2.55 (Table 7.1) and KiCad's IPC EP is 2.6. Marked `inferred`.
- **`ep_size` from D2 and E2.** Printed as two separate rows (2.35 / 2.45 / 2.55 each) with identical values. The EP is
  square, and `ep_size` is one side length, so both rows collapse into one min/nom/max.
- **`body_length` = D = 4.00 and `body_width` = E = 4.00.** Both `BSC`; the package is square 4.0 × 4.0 mm. Confirmed
  against the silkscreen outline in Figure 7.1 and against KiCad's `F.Fab` 4 × 4 mm rectangle.
- **`height` = A, `standoff` = A1, `lead_width` = b, `lead_length` = L.** Read off Figure 7.1 on page 37: `A` spans the
  full body+lead stack from the seating plane, `A1` is the gap from the seating plane C to the body underside, `b` is the
  lead width (confirmed in DETAIL "A" at the bottom of the same drawing), `L` is the foot length measured from the body
  edge to the lead tip. `aaa`/`bbb`/`ccc`/`ddd` are datums/true-position tolerances and have no slot in the dimension
  name list, so they are left out.
- **`land_*` values recorded as `nom`.** Table 7.2 has Min/Max columns but every land value is a single number in the
  "Max" column — these are reference land-pattern dimensions, not limits. The skill's rule for "one number in a land
  pattern" is `nom`.
- **Pin 1 split.** Table 5.2 prints the name as `RI / CLK` with two description lines (`Digital Input. Ring
  Indicator…` / `Digital Output. Clock output.`), and Table 4.2 note 1 on page 19 confirms "On QFN28 and QFN24 packages, the CLK
  signal is available on the same pin as RI." → `bidirectional`, name `RI`, `alt_names` `["CLK"]`.
- **Pin 25 number.** The datasheet gives the pad position as `Center` with no pin number, so the number `25`
  (= `pin_count + 1`) is assigned per the skill's exposed-pad rule and the pin is `inferred`.
- **Pin 6 `VDD` as `power_in`.** The description "Supply Power Input / 5V Regulator Output" names two roles. The primary
  role is the device supply input (the 5 V regulator output is the alternate use when the internal regulator is enabled),
  so `power_in`. Matches KiCad.
- **Pins 11–14 `alt_names`.** The second function is an alternate function of the same pin, so it goes in `alt_names`,
  not in the name. `GPIO.0`–`GPIO.3` keep the datasheet's printed order as primary.
- **`group` omitted throughout.** This part has no separate identical units (contrast the LM358 case's `A`/`B`); supply
  and ground pins are grouped with everything else.
- **`status` policy.** `extracted` only where the datasheet prints a direction ("Digital Input", "Digital Output",
  "Digital Input/Output", "No Connect") or an explicit supply role. `inferred` for pins 2, 3, 4, 5, 6, 7, 9, 25 and for
  `land_span` / `land_ep_size` — 10 `inferred` entries in total, which is what the validator reports.

## 3. Datasheet self-contradictions

No material contradiction was found. Checked and clean:

- **Figure 5.2 vs Table 5.2** (page 29/30): all 24 numbers, names and the pin-1 corner marker agree; verified
  number-by-number on the rendered page. No second QFN24 view exists, so there is no cross-package confusion.
- **Table 5.2 vs Table 4.2** (page 19): the QFN24 column of the GPIO alternate-function table (`GPIO.0=TXT`,
  `GPIO.1=RXT`, `GPIO.2=RS485`, `GPIO.3=WAKEUP`) matches pins 14/13/12/11.
- **`VSS` vs `GND` on the bottom pad**: Revision 1.1 (page 46) records "Updated QFN24 bottom pad label to GND instead of
  VSS." A grep of the whole PDF finds `VSS` only in that changelog line; the QFN24 centre pad is labelled `GND` in
  Table 5.2 and in Figure 5.2. Consistent.
- **Ordering table vs pin table**: page 2 states QFN24 has 4 GPIOs and separate VIO/VDD pins, which is what pins 5, 6
  and 11–14 deliver.

Two things that look like contradictions but are not, recorded so a reviewer does not re-litigate them:

- **Figure 7.2 is not to scale with Table 7.2.** Measured against the drawing's own 0.5 mm pitch, the drawn C1/C2 span
  is ~4.0 mm (table: 3.90) and the drawn centre pad is ~2.65 mm (table: 2.55). The drawing is schematic in those two
  places; the table governs and the numbers were taken from the table.
- **Page 2 note 1** ("Devices with the same ordering part number may have different types of pin 1 indicators")
  is a real caveat about the part, not an inconsistency in the data: it means the land pattern is unchanged whichever
  indicator the manufacturer fitted. It does not affect this spec.

## 4. Result

- `kicad-partspec validate spec.gold.json --datasheet cp2102n.pdf` → `passed: true`, 0 failures (10 `status.inferred`
  warnings, as expected).
- `kicad-partspec build spec.gold.json --out out --concise` → `passed: true`, 0 failures, 0 `footprint.skipped`.
  Produced `out/CP2102N-A02-GQFN24.kicad_sym` and
  `out/partspec.pretty/QFN-24-1EP_4x4mm_P0.5mm_EP2.55x2.55mm.kicad_mod`.
- The generated footprint pads sit at ±1.95 with size 0.85 × 0.30 and a 2.55 × 2.55 EP — i.e. the datasheet's own land
  pattern, not KiCad's IPC-derived one, as intended.
