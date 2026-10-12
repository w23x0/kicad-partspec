# ULN2003A (TSSOP-16) — gold review

Datasheet: `uln2003a.pdf`, SHA-256 `ba83a908675b45c41e84fb06ea390efb10f4b7a358edfee656f87a968dd1d62f`,
**SLRS027T (Rev. T, March 2025)** (confirmed on every page footer and in the Revision History on PDF page 21).

Package asked for: **TSSOP-16**, TI drawing code **PW0016A** — package outline on PDF page 38,
example board layout (land pattern) on page 39, example stencil design on page 40.
The same datasheet also carries NS0016A (SOP, pages 31–33) and DYY0016A (SOT-23-THIN, pages 35–37);
those were ignored. Every dimension and pin below was read from the text layer and then confirmed on the
rendered image of the page cited (p.3 at 200 dpi, p.38 and p.39 at 200 dpi plus 400 dpi crops of the top
view and Detail A).

## 1. Disagreements with the official KiCad library

Symbol: `/usr/share/kicad/symbols/Transistor_Array.kicad_sym`, `ULN2003A` → `extends "ULN2003"`, so the
pins live in the parent symbol. Footprint: `Package_SO:TSSOP-16_4.4x5mm_P0.65mm`.

| # | Item | Datasheet | KiCad | Decision | Page |
|---|---|---|---|---|---|
| 1 | Pin names 1–7 | `1B` `2B` `3B` `4B` `5B` `6B` `7B` (Table 4-1 and Figure 4-1) | `I1`…`I7` | **Datasheet.** KiCad's `I` for "input" renames the pin; the datasheet's own labels are `nB` ("base of channel n"). Numbers and pairing are identical, so only the label text differs. | 3 |
| 2 | Pin name 8 | `E` | `GND` | **Datasheet.** `E` is the printed name; "typically tied to ground" is the datasheet's own description, not part of the name. | 3 |
| 3 | Pin names 10–16 | `7C` `6C` `5C` `4C` `3C` `2C` `1C` | `O1`…`O7` (O1 on pin 16, … O7 on pin 10) | **Datasheet.** Same renumbering as row 1, mirrored on the collector side. KiCad's number→name mapping is equivalent (`O1`=pin 16 ↔ `1C`=pin 16), so there is no pinout conflict, only label text. | 3 |
| 4 | Pin 9 `COM` — type | I/O column is an em dash, "no direction printed"; description: "Common cathode node for flyback diodes" | `passive` | **Agree — `passive`**, status `inferred` (no direction printed). | 3 |
| 5 | Pin 8 `E` — type | "Common emitter shared by all channels (typically tied to ground)", I/O column an em dash | `power_in` | **Agree — `power_in`**, status `inferred` (ground rule). | 3 |
| 6 | Pins 1–7 — type | I/O column `I`, "Channel 1 through 7 Darlington base input" | `input` | **Agree — `input`**, status `extracted`. | 3 |
| 7 | Pins 10–16 — type | I/O column says **`O`** and footnote (1) defines `O = Output`; but the Detailed Description says "All units feature a common emitter and **open collector outputs**" | `open_collector` | **`open_collector`**, status `inferred` — agreeing with KiCad, because the skill's rule is that the function description outranks the bare direction column, and the datasheet uses the words "open collector outputs" outright. See §3 item 1 for the datasheet's internal tension here. | 3 (column) / 14 (description) |
| 8 | Pad size | land pattern `16X (1.5)` × `16X (0.45)` = 1.5 × 0.45 mm | pads 1.475 × 0.400 mm | **Datasheet for the `land_*` dimensions** (1.5 × 0.45, nom). The KiCad size is IPC-7351-derived, which the task statement says may legitimately differ; both round to the same IPC density class. | 39 |
| 9 | Pad-row spacing | land pattern `(5.8)` centre-to-centre | pads at x = ±2.8625 → 5.725 mm | **Datasheet — `land_span` 5.8 nom.** The 0.075 mm difference is IPC-7351 vs the TI land pattern, not a conflict. | 39 |
| 10 | Pitch | `14X 0.65` on both the outline and the land pattern | 0.65 mm | **Agree.** | 38, 39 |
| 11 | Body size | 4.9–5.1 (along the pin rows) × 4.3–4.5 (across the rows) | footprint name `4.4x5mm` (nominal 4.4 × 5.0) | **Agree.** The stacked pairs centre on 5.0 and 4.4; the builder names the generated footprint `TSSOP-16_4.4x5.0mm_P0.65mm`, KiCad writes `4.4x5mm`. Naming only. | 38 |
| 12 | Overall lead span | `6.6` stacked over `6.2 TYP`, tip to tip across the rows (a min/max pair — see §2 item 1) | no overall span in the footprint (courtyard is ±3.6 = 7.2 mm, which includes pad plus 0.5 mm margin) | Not comparable; the datasheet value is recorded as `overall_width` 6.2 / 6.6. | 38 |

Ten of the twelve rows are label or IPC-vs-datasheet differences; **no KiCad pin number or pinout ordering
disagrees with the datasheet.**

## 2. Values that had to be interpreted

Dimensions (all on PDF page 38 unless stated):

1. **`overall_width` 6.2 / 6.6 (min/max)** — the drawing stacks `6.6` over `6.2 TYP` above the top view. The
   extension lines run from the left lead tips to the right lead tips, i.e. tip to tip *across* the rows,
   which is the largest across-rows dimension on the outline. Recorded `min`/`max`, the same top=max/bottom=min
   stacked pair this sheet uses for `5.1/4.9`, `4.5/4.3`, `0.30/0.17`, `0.75/0.50` and `0.15/0.05`; the `TYP`
   here is the sheet's usual annotation on the lower limit, not a separate nominal, and the midpoint (6.4) is
   printed nowhere. Marked `inferred`.
2. **`body_length` 4.9 / 5.1** — the `5.1 / 4.9 NOTE 3` dimension is the *vertical* one on the top view,
   i.e. along the pin rows (pin 1 to pin 8). NOTE 3 is the mold-flash note, which applies to the package
   ends, confirming it is the length along the row. The drawn body is taller than it is wide (765 px vs
   685 px), consistent with 5.0 long × 4.4 wide.
3. **`body_width` 4.3 / 4.5** — the `4.5 / 4.3 NOTE 4` dimension at the bottom, *across* the rows.
   NOTE 4 (interlead flash, 0.25 mm/side) applies to the lead-bearing sides, confirming the direction.
4. **`lead_width` 0.17 / 0.30** — `16X 0.30 / 0.17`, drawn across the width of a lead.
5. **`lead_length` 0.5 / 0.75** — Detail A. The horizontal dimension between the toe and where the fillet
   starts is the flat foot resting on the board, so it is `lead_length` and not the body-to-tip length.
   No such length is otherwise given. Marked `inferred`.
6. **`standoff` 0.05 / 0.15** — Detail A. The vertical dimension between the dashed gage plane and the
   underside of the lead foot, with the seating plane below: that gap is the standoff. Marked `inferred`.
7. **`height` 1.2 max** — `1.2 MAX` on the side view, measured overall from the seating plane. Read
   directly; also the drawing's own title ("TSSOP - 1.2 mm max height").
8. **`pitch` 0.65 nom** — `14X 0.65`, boxed as a basic dimension. Confirmed as a pitch by counting seven
   gaps between pins 1 and 8 (= 4.55, which is exactly the separate `2X 4.55` callout).

Deliberately **left out**:

9. **`2X 4.55`** — this is the lead *centre-to-centre* span along one row (7 × 0.65). `reference.md` says a
   lead centre-to-centre span is not recorded, and it is not an overall size.
10. **`0.25 GAGE PLANE`** — a datum height, not a part size.
11. **`(0.15) TYP`** lead chamfer, **`0.1 C`** coplanarity, **`4X (0°-12°)`** lead angle, **`0°-8°`** toe
    angle — angles and chamfers are outside the dimension vocabulary.
12. **`1.2 MAX` vs the drawing title** agree, so only one entry was made.

Land pattern (PDF page 39):

13. **`land_pad_length` 1.5 nom** — `16X (1.5)` is the pad extent *away from* the package centreline, i.e.
    along the lead direction. (Reference value in parentheses; parentheses are allowed for `land_*`.)
14. **`land_pad_width` 0.45 nom** — `16X (0.45)` is the pad extent along the row.
15. **`land_span` 5.8 nom** — `(5.8)`, drawn between the two pad centreline axes. Marked `inferred`
    because the drawing labels it only as a bare number between two rows of pads. This matches the
    `lm358_soic8` gold, which marks its `(5.4)` the same way.
16. **`(R0.05) TYP` pad corner radius, `0.05 MAX`/`0.05 MIN` solder-mask clearance** — not package
    dimensions and not in the vocabulary.

Pins and package:

17. **Types of pins 1–7.** The I/O cell is merged across seven rows and the letter `I` is printed only on
    the `4B` row. Read as `input` for all seven from the merged cell plus the description "Channel 1
    through 7 Darlington base input"; status `extracted` because the column and the description both say so.
18. **Types of pins 10–16.** Same merged-cell situation for the `O` on the `4C` row, but the type recorded
    is `open_collector`, taken from the sentence "All units feature a common emitter and open collector
    outputs" on PDF page 14. Marked `inferred` (the skill makes every open-collector choice inferred).
19. **Pin 8 `E`** → `power_in` by the ground rule (the datasheet says "typically tied to ground").
20. **Pin 9 `COM`** → `passive` by the no-direction rule (the I/O column is an em dash).
21. **`package.family` = `TSSOP`.** The datasheet's names for the package are the code `PW` and the string
    "TSSOP": Figure 4-1's caption ("D, N, NS, and PW Package 16-Pin SOIC, PDIP, SO, and TSSOP Top View",
    page 3), the thermal table's column header `PW (TSSOP)` (page 4), and the drawing title
    "TSSOP - 1.2 mm max height" (page 38). The whole datasheet covers five package options; only PW is
    used here.
22. **`group` on every pin.** The part is seven identical Darlington channels and the datasheet numbers them
    (`1B`/`1C` … `7B`/`7C`), so the key is the datasheet's own channel number: pins 1–7 get `"1"`…`"7"` and
    pins 16–10 get `"1"`…`"7"` to match, so `1B` (pin 1) and `1C` (pin 16) share the key `"1"` — the two sides
    of one channel are one block. Pin 8 `E` (the common emitter shared by all channels) and pin 9 `COM` (the
    common cathode node) both take `"power"`, the key `reference.md` names for supply/ground pins. The
    reference gives `"A"`/`"B"` only as *examples* of a key; it does not require letters. No new evidence
    quote is added: the pins already cite page 3, which is where the channel numbering and the
    common-emitter/common-cathode descriptions are printed, and see "Round-4 corrections" below for the
    p.1/p.14/p.15 wording.
    `group` says nothing about how a pin's number, name or type was read, so no pin's `status` changed.
23. **Pin-number-to-name pairing** was confirmed twice on the rendered image of page 3: Figure 4-1 (top
    view, pin 1 top-left, running clockwise: `1B` 1 … `7B` 7, `E` 8, `COM` 9, `7C` 10 … `1C` 16) and
    Table 4-1 (which lists `1B`…`7B` on numbers 1–7, `1C`…`7C` on numbers 16–10, `COM` on 9, `E` on 8).
    The figure and the table agree with each other and with the gold.
24. **Quotes that drag an interleaved token.** For the stacked pairs on page 38 the text layer prints the
    neighbouring callout between the two numbers, so the quote has to include it: `"5.1 4.55 4.9 NOTE 3"`
    and `"4.5 16X 1.2 MAX B 0.17 4.3"` and `"0.30 4.5 16X 1.2 MAX B 0.17"`. Each quote is the shortest
    run of the page's own token order that contains both numbers of that dimension; the stray `4.55`,
    `16X`, `1.2 MAX` and `B` belong to the other callouts and were confirmed as such on the image.

## 3. Places where the datasheet contradicts itself

1. **Output type (real tension).** Table 4-1 prints `O` in the I/O column for pins 10–16 and footnote (1)
   defines `O = Output`, while the Detailed Description on page 14 says the units "feature a common emitter
   and open collector outputs". The gold follows the description (`open_collector`), because the skill is
   explicit that the direction column is not the last word, and because KiCad agrees. Note that the part is
   physically a Darlington *sink* driver with an internal base-emitter path, so "open collector" is the
   datasheet's loose wording rather than a strict electrical description — but the datasheet is the source
   of record here and it says "open collector outputs" in so many words.
2. **`COM` "required" vs "can be left floating" (apparent only).** Table 4-1 calls the COM pin
   "required for inductive loads"; §7.4.2 on page 15 says "The COM pin can be left floating" for resistive
   loads. These are different applications, so there is no real contradiction, but the phrasing invites one.
3. **Lead span `TYP` does not centre on JEDEC.** Note 5 of drawing PW0016A references JEDEC registration
   MO-153. The body dimensions do centre on the JEDEC nominals (4.9/5.1 → 5.0, 4.3/4.5 → 4.4), but the
   overall lead span is printed `6.6` over `6.2 TYP`, whose 6.2 does not centre on MO-153's 6.4 nominal
   lead span, and whose TYP is tighter than a typical value usually is. The gold records the printed pair
   as limits (`min` 6.2, `max` 6.6, §2 item 1) rather than inventing a 6.4 nominal.
4. **`Clamp diode reverse voltage` (page 4)** is given in the Absolute Maximum Ratings table with no
   parameter symbol and no separate MIN/MAX columns — a formatting inconsistency in the table, not a
   conflict in a value. It is not a package or pin fact, so it does not enter the spec.
5. **Figure 4-1 is shared by four packages** (D, N, NS, PW) and prints one name/number set for all of them.
   The pinout is identical across those packages in this datasheet, so there is nothing to disambiguate, but
   it means a name taken from the figure cannot be attributed to "TSSOP only". Confirmed against the PW-only
   outline drawing (PW0016A, pins 1 and 8 down the left side, 16 and 9 down the right, pins 1–8 down each
   row), which matches.

## 4. Result

- 16 pins, all confirmed against Table 4-1 and Figure 4-1 on PDF page 3.
- 11 dimensions: 8 from the package outline (`pitch`, `body_length`, `body_width`, `overall_width`,
  `height`, `standoff`, `lead_width`, `lead_length`) and 3 from the land pattern (`land_pad_length`,
  `land_pad_width`, `land_span`).
- A footprint **was** generated: `out/partspec.pretty/TSSOP-16_4.4x5.0mm_P0.65mm.kicad_mod`, pads at
  x = ±2.9, y = ±2.275 in steps of 0.65, pad size 1.5 × 0.45 — the datasheet's own land pattern.
- `kicad-partspec validate spec.gold.json --datasheet uln2003a.pdf` → `passed: true`.
- `kicad-partspec build spec.gold.json --out out --concise` → `passed: true`, 0 failures, 13 warnings, all
  of kind `status.inferred` (9 pins: `E`, `COM`, `7C`…`1C`; 4 dimensions: `overall_width`, `standoff`,
  `lead_length`, `land_span`).

## Round-4 corrections

Two changes were made to this gold after the extraction runs were reviewed; nothing else was re-read or
re-decided.

1. **`group` added to all 16 pins** (§2 item 22 was rewritten accordingly). The part is seven identical
   Darlington channels, and the runs keyed them by the datasheet's own channel numbers, which is right —
   the earlier gold had left `group` off because no unit *letters* are printed, but `reference.md` offers
   `"A"`/`"B"` only as examples of a key. Pins 1–7 (`1B`…`7B`) take `"1"`…`"7"`, pins 16–10
   (`1C`…`7C`) take `"1"`…`"7"` so that both sides of a channel share one key, and pins 8 (`E`) and
   9 (`COM`) take `"power"`. Evidence: p.1 "Each consists of **seven NPN Darlington pairs**"; p.14 §7.1
   "seven high-voltage, high-current NPN Darlington transistor pairs … Each channel"; p.15 §7.3 "Each
   channel of the ULN2003A device consists of Darlington connected NPN transistors". The pins already cite
   page 3, where the channel numbering and the common-emitter/common-cathode descriptions are printed, so
   no new quotes were added and no pin's `status` changed.
2. **`overall_width` `nom`/`max` → `min`/`max`** (§2 item 1, §3 item 3 and KiCad row 12 updated to match).
   `6.6` over `6.2 TYP` is the same top=max/bottom=min stacked pair this sheet uses for `5.1/4.9`,
   `4.5/4.3`, `0.30/0.17`, `0.75/0.50` and `0.15/0.05`. A nominal equal to the lower limit of its own
   range is not a reading any convention supports, and the midpoint 6.4 is printed nowhere. Status stays
   `inferred`; page and quote are unchanged.
