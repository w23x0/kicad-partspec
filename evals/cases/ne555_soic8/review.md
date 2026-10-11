# NE555 (TI SLFS022K) — gold review

Datasheet: `ne555.pdf`, sha256 `a3756e59fd06d0ba736edf9ffe71d99d2aae33fb7e49fedc86165a241179f4a6`,
`https://www.ti.com/lit/ds/symlink/ne555.pdf`, revision **SLFS022K (Rev. K, March 2026)** — read from the page-1
header line `SLFS022K – SEPTEMBER 1973 – REVISED MARCH 2026` and confirmed by the Revision History table on PDF
page 22 ("Changes from Revision J (February 2025) to Revision K (March 2026)").

Package used: **D (SOIC, 8)**, drawing **D0008A** on PDF pages 30 (outline), 31 (land pattern), 32 (stencil).
Pages 24–29 (P0008A / PDIP) and 36–38 (PW0008A / TSSOP) are other packages and were ignored.

## 1. KiCad disagreements

Cross-checked against `/usr/share/kicad/symbols/Timer.kicad_sym` symbol **NE555D** (the SOIC-8 variant;
`NE555P` `extends` `NE555D` and only overrides the footprint, so its pins are the same) and
`/usr/share/kicad/footprints/Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod`.

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| 1 | Pin 4 name | `RESET` (Table 4-1 and the top-view pinout figure both print `RESET`) | `~{RST}` | Gold uses `RESET`. KiCad's `~` encodes active-low, which the datasheet states in words ("Active low reset input forces output and discharge low."); it is an abbreviation of the same primary name, not a different function. | 3 |
| 2 | Pin 5 `CONT` type | Table 4-1 TYPE = **Input/output** | `open_collector` | Gold uses **`bidirectional`**, status `extracted`. The datasheet's own type column says "Input/output" and the skill maps I/O to `bidirectional`. KiCad's `open_collector` is a modelling choice for the same net; the datasheet never calls CONT open-collector (that word appears only on the `DISCH` row). | 3 |
| 3 | Pin 7 `DISCH` type | Table 4-1 TYPE = **Output**, DESCRIPTION = "**Open collector** output to discharge timing capacitor" | `input` | Gold uses **`open_collector`**, status `inferred` (per the skill's open-drain/open-collector rule). KiCad's `input` is flatly contradicted by the datasheet: DISCH sinks the timing capacitor current whenever the output is low, and the Description section on PDF page 1 says "a low-impedance path is provided between the discharge pin (DISCH) and the ground pin (GND)". Datasheet wins. | 3 (and 1) |
| 4 | Land pad length | `8X (.061) [1.55]` | pad size 1.95 mm (IPC-7351 nominal) | Gold uses **1.55 mm** from the TI land pattern. Pad size legitimately differs: KiCad's generator uses IPC-7351 density level B, not the vendor land pattern. Not an error on either side. | 31 |
| 5 | Land pad row span (`land_span`) | `(.213) [5.4]` | pad centres at x = ±2.475 → 4.95 mm | Gold uses **5.4 mm** from the TI land pattern, marked `inferred` (the drawing does not literally say "centre-to-centre"; the dimension line runs between the two pad centrelines). Same IPC-vs-vendor-land-pattern explanation as #4. | 31 |
| 6 | Lead width | `8X .012-.020 [0.31-0.51]` | (not carried in the footprint) | No conflict. Recorded 0.31–0.51 mm. | 30 |

Agreements worth recording (no action): pad count 8/8; pitch 1.27 mm (identical); KiCad fab body 3.9 × 4.9 mm
vs datasheet body 3.81–3.98 × 4.81–5.00 mm (inside KiCad's rounding); KiCad footprint filter
`SOIC*3.9x4.9mm*P1.27mm*` matches the D0008A package; pin numbering 1–8 identical; GND/VCC/TRIG/THRES/OUT names
identical. The generated footprint from this gold is `SOIC-8_3.9x4.9mm_P1.27mm`, i.e. the same name KiCad uses,
but built from TI's land pattern (pad 1.55 × 0.6 at x = ±2.7) rather than IPC-7351.

## 2. Interpretations

1. **`land_span` = 5.4 mm, status `inferred`.** The land-pattern drawing gives `(.213) [5.4]` with no word
   saying what it measures. On the rendered page the dimension line runs horizontally between the vertical
   centreline of a left pad and the vertical centreline of the matching right pad, so it is a centre-to-centre
   span between the two pad rows — `land_span` in the reference's list. Parenthesised ⇒ reference value ⇒ `nom`.
2. **`lead_thickness` = 0.13–0.25 mm, status `inferred`.** D0008A prints `.005-.010 TYP [0.13-0.25]` on page 30.
   On the rendered page the arrows cross the lead toe of the front view, so the callout is measured across the
   lead material — `lead_thickness` in the reference's dimension list. The bracketed millimetre range is recorded
   as min/max; `TYP` qualifies the inch form only, which is how `overall_width` above is treated as well. The
   status is `inferred` because the drawing carries no name for the dimension and its identity had to be
   interpreted from where the arrows land, not read from a table row.
3. **`standoff` = 0.11–0.25 mm, status `inferred`.** D0008A prints `.004-.010` with `[0.11-0.25]` on page 30, in
   Detail A. On the page at 600 dpi this one resolves cleanly: a dash-dot extension line runs from the body
   underside to an extension line at the seating plane, so the callout is the gap between the body underside and
   the seating plane — `standoff` in the reference's dimension list. (The page's text layer also prints the
   `0 -8` draft-angle callout between the inch and millimetre forms, so the quote is
   `.004-.010 0 -8 [0.11-0.25]` — verbatim as printed.) Status `inferred` for the same reason as
   `lead_thickness`: the drawing names no dimension, so which callout this is had to be read off the geometry.
   Both are recorded rather than left out: under the skill and `reference.md` a dimension that resolves from the
   drawing is recorded, and `inferred` is exactly the status for one whose meaning had to be interpreted.
4. **`2X .150 [3.81]` deliberately omitted.** This is the lead centreline-to-centreline span across the two rows
   in the outline drawing. The reference explicitly says a lead centre-to-centre span is not recorded (it would
   be neither `overall_width` nor `body_width`), and it is not a land-pattern value, so it is not `land_span`.
5. **`.041 [1.04]` (Detail A) and `.010 [0.25]` (Detail A) omitted** — reference/detail geometry with no name in
   the reference's dimension list.
6. **`overall_width` = 5.80–6.19 mm** taken from `.228-.244 TYP`, the lead tip-to-tip span across the rows, which
   is the largest across-rows dimension on the outline. `TYP` on the inch value does not make it a nominal: the
   inch and millimetre forms are the same range, so it is recorded as min/max (this matches the LM358 gold for the
   identical D0008A drawing).
7. **Pin types chosen through the skill's derived rows** (`inferred`): `GND` and `VCC` have `—` in the TYPE column
   → `power_in`; `DISCH` is `output` in the TYPE column but the description says "Open collector output"
   → `open_collector`. `CONT` is `Input/output` → `bidirectional`, which the skill treats as read from a printed
   direction, so it stays `extracted`.
8. **No `group` on any pin.** The 555 is a single functional block; only the supply pair would qualify for
   `power`, and the round-2 gold cases (ina219_soic8, tps54202_sot23, ads1115_vssop10, txs0108e_tssop20,
   stm32g030_tssop20, cp2102n_qfn24) all omit `group` for a lone supply pair. Only the round-1 lm358 gold uses
   `group: "power"`, in a part that also has two real units (`A`/`B`).
9. **No `alt_names` anywhere.** No pin has a second function. `RESET`'s active-low polarity is stated in prose,
   which is a polarity, not an alternate function.
10. **`NC` row of Table 4-1 contributes no pins.** Its "D (SOIC)…" column is `—`; the NC numbers (`1, 3, 4, 6, 8,
   9, 11, 13, 14, 16, 18, 19`) are all FK (LCCC, 20) pins. Confirmed on the rendered page: the FK figure is the
   only drawing with NC labels, and the D-package figure has all 8 pins named.
11. **Pin 5's `CONT` is not an analog reference.** The skill would map a plain "analog reference" pin to
    `passive`, but this pin prints a direction ("Input/output"), so the direction wins over the passive rule.
12. **Family `SOIC`, `mpn` `NE555`.** The datasheet names the package "D (SOIC)" and the drawing title is
    "SOIC - 1.75 mm max height". `NE555` is the device name; the SOIC orderables are `NE555DR` / `NE555DRG4`, but
    the gold uses the base part number as `lm358_soic8` does for the SOIC-8 LM358 case.
13. **`.008 [0.2]`-class pin-1 identifier and the 0°–8° / 0°–15° draft angles, the solder-mask expansion
    (`.0028` max/min), and the paste aperture note were all skipped** — none maps to a name in the reference's
    dimension list.

## 3. Self-contradictions in the datasheet

Nothing material was found. Checked specifically:

- **Pinout figure vs Table 4-1:** agree on all 8 D-package pins (1 GND, 2 TRIG, 3 OUT, 4 RESET, 5 CONT, 6 THRES,
  7 DISCH, 8 VCC). Verified on the rendered page 3.
- **Page-1 simplified schematic pin numbers vs Table 4-1:** agree (1, 2, 3, 4, 5, 6, 7, 8 all consistent).
- **FK NC list:** Table 4-1 lists 12 NC pins for the FK package; the FK figure on page 3 shows exactly those 12
  NC positions (1, 3, 4, 6, 8, 9, 11, 13, 14, 16, 18, 19) with GND/CONT/VCC/RESET/TRIG/OUT/THRES/DISCH
  elsewhere. Consistent.
- **Package heading vs pin-table column header:** the figure caption lists "NE555...D, P, PS, OR PW PACKAGE" while
  Table 4-1's column reads "D (SOIC), P (PDIP), PS (SO), PW (TSSOP), JG (CDIP)" — the figure caption omits `JG`,
  which the table includes for SE555. This is an omission in a caption, not a conflict about any pin of the SOIC
  package, and it changes nothing here.
- **"TTL-compatible output can sink or source up to 200mA" (Features, page 1) vs `IO` = ±200 mA recommended and
  ±225 mA absolute maximum:** consistent (recommendation inside the absolute maximum).
- **`CONT` description says "Outputs 2/3 × VCC"** while the Threshold/Trigger levels in the Description are
  "approximately two-thirds" and "approximately one-third" — the Description adds "approximately", so the two
  statements agree; the CONT row is the idealised value.

## 4. Report

- **Pins:** 8 (D SOIC-8: 1 GND, 2 TRIG, 3 OUT, 4 RESET, 5 CONT, 6 THRES, 7 DISCH, 8 VCC). No exposed pad, no NC.
- **Dimensions:** 12 (9 from the package outline on page 30: pitch, overall_width, body_length, body_width,
  height, lead_width, lead_length, lead_thickness, standoff; 3 from the land pattern on page 31: land_pad_length,
  land_pad_width, land_span). `lead_thickness`, `standoff` and `land_span` are `inferred`; the other 9 are
  `extracted`.
- **Footprint:** generated. `out/partspec.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod` — 8 pads, 1.27 mm pitch,
  1.55 × 0.6 mm pads at x = ±2.7 mm, from the datasheet's own land pattern.
- **KiCad disagreements:** 6 (#1–#6 above). #1 decided for the datasheet's spelling (`RESET` vs `~RST`);
  #2 and #3 decided for the datasheet's TYPE/DESCRIPTION column (`CONT` bidirectional rather than
  `open_collector`; `DISCH` `open_collector` rather than KiCad's `input`); #4 and #5 are the expected
  IPC-7351-vs-vendor-land-pattern pad-length and row-span difference, with the datasheet's land pattern kept;
  #6 is not a conflict.
- **Validation:** `kicad-partspec validate` passes (6 `status.inferred` warnings only) and
  `kicad-partspec build` passes with 0 failures and those same 6 warnings.

## Round-4 corrections

Applied after this gold was hand-checked, per the round-4 adjudication. Two dimensions that the first pass had
left out because the callouts on page 30 could not be assigned to a name are now recorded. Nothing else in the
spec changed.

- **`lead_thickness` added**, `min` 0.13 / `max` 0.25, `status: inferred`. Source: page 30, quote
  `.005-.010 TYP [0.13-0.25]`. The arrows cross the lead toe in the D0008A front view, so the callout measures
  across the lead material. Placed in `package.dimensions` directly after `lead_length`.
- **`standoff` added**, `min` 0.11 / `max` 0.25, `status: inferred`. Source: page 30, quote
  `.004-.010 0 -8 [0.11-0.25]`. In DETAIL A the dimension runs from a dash-dot extension line at the body
  underside to an extension line at the seating plane, i.e. the standoff. At 600 dpi this callout resolves
  cleanly, so under the skill and `reference.md` it is recorded rather than omitted. The quote carries the `0 -8`
  draft-angle callout because page 30's text layer prints it between the inch and millimetre forms of the same
  dimension; the value is unchanged.

Both carry `inferred` because the drawing names neither dimension — assigning each callout to a name in the
reference's dimension list was an interpretation, which is exactly what `inferred` is for. §2 items 2 and 3 now
describe the two dimensions; the previous §2 item 2, which said both were deliberately omitted, is replaced.