# TXS0108E / PW (TSSOP-20) — gold PartSpec review

Datasheet: `txs0108e.pdf`, SHA-256 `a6ddbe03…25c883` (matches `source.txt`), SCES642L, Rev. L,
December 2007 – revised November 2024. 42 pages.

Pages used: **3** (pin configuration figure, Fig. 4-3), **4** (Table 4-1 Pin Functions),
**28** (PW0020A package outline), **29** (PW0020A example board layout).

The other four packages in this datasheet (DGS0020A p.31/32, RGY0020C p.35/36, RKS0020A p.39/40,
NME0020A p.42 area) were **not** used.

## 1. Disagreements with the official KiCad library

Cross-checked against:

* Symbol `TXS0108EPW`, `/usr/share/kicad/symbols/Logic_LevelTranslator.kicad_sym` line 19542
  (self-contained, does **not** extend a parent symbol — all 20 pins are in `TXS0108EPW_1_1`).
* Footprint `Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm`,
  `/usr/share/kicad/footprints/Package_SO.pretty/TSSOP-20_4.4x6.5mm_P0.65mm.kicad_mod`
  (`descr` says "generated with kicad-footprint-generator ipc_gullwing_generator.py", JEDEC
  MO-153 Var AC — i.e. IPC-7351 geometry, not this datasheet's land pattern).

### 1.1 Pin and dimension agreement summary

| Check | Gold | KiCad | Result |
|---|---|---|---|
| pin count | 20 | 20 pads / 20 symbol pins | agree |
| pin numbers ↔ names | 1 A1, 2 VCCA, 3 A2 … 11 GND, 12 B8 … 20 B1 | identical | agree (all 20) |
| pin electrical types | 16 `bidirectional`, 1 `input` (OE), 3 `power_in` | 16 `bidirectional`, 1 `input`, 3 `power_in` | agree (all 20) |
| pitch | 0.65 | 0.65 (pad y-step) | agree |
| body size | 6.4–6.6 × 4.3–4.5 (nom 6.5 × 4.4) | F.Fab 6.5 × 4.4 | agree |
| height | 1.2 max | not modelled | n/a |
| pad size | land 1.5 × 0.45 | 1.475 × 0.4 | differ (see 1.2) |
| land span | 5.8 | 5.725 | differ (see 1.2) |

There were **no disagreements about pins, pin numbers, pin names, pin types, pitch or body size.**
Every one of the 20 pins was checked one by one against the rendered page and against KiCad.

### 1.2 The only disagreements: land-pattern pad size and span

| Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|
| `land_pad_length` | 1.5 (`20X (1.5)`) | 1.475 (IPC-7351 nominal density) | **Datasheet** (1.5) | 29 |
| `land_pad_width` | 0.45 (`20X (0.45)`) | 0.4 (IPC-7351) | **Datasheet** (0.45) | 29 |
| `land_span` | 5.8 (`(5.8)`, pad centre to pad centre) | 5.725 (IPC-7351, row centres ±2.8625) | **Datasheet** (5.8) | 29 |

The task statement already anticipates this: *"KiCad pads come from IPC-7351 rather than the
datasheet land pattern, so pad SIZE may legitimately differ."* The KiCad `descr` field confirms its
pads are IPC-7351 generated, not copied from the PW0020A land pattern. Per `reference.md`,
`land_*` values come **only** from the datasheet's example land pattern, so the gold keeps 1.5 /
0.45 / 5.8 and the built footprint pads land at exactly those values (pads at x = ±2.9, size
1.5 × 0.45, pitch 0.65).

Note also that 5.8 is *not* the same quantity as the package-outline `2X 5.85` (row **lead
centreline** spacing on p.28); the land pattern pad centres are 5.8 apart. They are separate
dimensions on separate pages and were kept separate.

## 2. Values that had to be interpreted

### 2.1 `overall_width` = 6.2 … 6.6, and why not `nom`

The top view of PW0020A carries a stacked callout `6.6` over `6.2 TYP`, on the dimension line
that runs **lead tip to lead tip across the two pin rows** (verified on the rendered image: its
extension lines land on the outer faces of pin 1 and pin 20).

* Per `reference.md`, for a dual-row package "across the rows is `overall_width`" — so this is
  `overall_width`, and there is **no** `overall_length` in the spec: the drawing never dimensions
  lead-tip-to-lead-tip along the rows as a separate quantity.
* `6.2` is printed with an explicit `TYP`, which TI does *not* do for the lower value of the other
  stacked pairs on this drawing (`6.4`, `4.3`, `0.19`, `0.50`, `0.05`). That argues `6.2` is a
  *typical*, i.e. `nom`. It is recorded as `min: 6.2, max: 6.6` because `reference.md` states
  without exception that "two numbers stacked on the drawing (1.0 over 0.8) gets min and max", and
  because for an outline dimension the resulting nominal outline is identical either way.
  **Flagged as a coin-flip for the human reviewer: `nom: 6.2` + `max: 6.6` is a defensible
  alternative reading.**

### 2.2 `body_length` = 6.4 … 6.6, and `body_width` = 4.3 … 4.5

Which stack is which was decided on the rendered image, not the text layer:

* The `6.6 / 6.4 NOTE 3` dimension is **vertical**, and its extension lines drop to the *top and
  bottom edges of the plastic body*. Note 3 is about mould flash, i.e. plastic. It is the body
  length along the pin rows (nominal 6.5). → `body_length`.
* The `4.5 / 4.3 NOTE 4` dimension is **horizontal**, and its extension lines drop to the *left and
  right edges of the plastic body*. Note 4 is about interlead flash, which grows inward from the
  lead roots on both sides into the gap between the two rows, so it is the body width across the
  rows (nominal 4.4, matching KiCad's `4.4x6.5mm`). → `body_width`.
* Geometry cross-check: row centreline spacing is `2X 5.85`; 5.85 − 4.5 = 1.35, i.e. 0.675 of lead
  foot per side, which sits inside the Detail A foot length `0.75 / 0.50`. Consistent.
* Both notes are only excluded-flash caveats, so the values are the true body extents.

### 2.3 `standoff` = 0.05 … 0.15 (marked `inferred`)

Detail A of PW0020A carries a `0.15 / 0.05` vertical callout drawn between the dotted **gage
plane** line and the solid **seating plane** line (datum C), next to a boxed `0.25 GAGE PLANE`.
The datasheet **does not label this callout**. It is recorded as `standoff` because it is the only
unaccounted-for dimension on the lead profile — every other Detail A callout is the lead length
(`0.75/0.50`), the lead thickness (`(0.15) TYP`), the foot angle (`0°-8°`) or the gage-plane note
itself — and because 0.05–0.15 is the standard gull-wing standoff for this package
(JEDEC MO-153), which the drawing cites. Marked `inferred` because the mapping is a reading of the
figure, not a printed label. **If a reviewer rejects it, deleting this one dimension is the whole
fix**; nothing else in the spec depends on it.

Deliberately **not** recorded from the same area of the drawing:

* `0.1 C` (concentricity of datum C) and the position tolerance frame `0.1Ⓜ | C | A | B` — these
  are geometric tolerances, not dimensions, and no PartSpec name fits them.
* `0.25 GAGE PLANE` — a note about where the gage plane is, not a size.
* `0.05 MAX / 0.05 MIN ALL AROUND` on p.29 — solder-mask tolerance, not a land dimension.

### 2.4 `lead_thickness` = 0.15, printed in parentheses

`(0.15) TYP` is a parenthesised (reference-only) value, and `reference.md` says parenthesised
values are certainly usable for `land_*` but does not bless them elsewhere. It is recorded as
`nom: 0.15` because the callout is unambiguous in meaning (lead thickness in the side view, arrowed
across the foot), and a `TYP` value is a nominal by definition. It does not affect the generated
symbol or footprint.

### 2.5 `land_span` = 5.8, marked `inferred`

`land_span` is the centre-to-centre distance between the two pad rows. On the rendered p.29 the
`(5.8)` dimension's extension lines drop to the **centrelines** of pads 1 and 20, which is what
makes it a span rather than an outer extent. Marked `inferred` for the same reason the
`lm358_soic8` gold marks its `land_span`: the reading of the callout is a figure interpretation.

### 2.6 `pitch` taken from the package outline

`18X 0.65` on p.28 (outline) is used for `pitch`; the land pattern repeats it as `18X (0.65)` on
p.29 with the identical value. `land_*` dimensions are restricted to the land pattern, so the
outline is the correct source for `pitch`. Both pages were checked; no ambiguity.

### 2.7 `OE` is `input`, not `tri_state`

The TYPE column of Table 4-1 prints `I` for pin 10, so `input`. The description
("Tri-state output-mode enable. Pull OE low to place all outputs in 3-state mode") describes what
the *outputs* do, not a three-state output pin. KiCad's symbol agrees (`pin input`). Status
`extracted`; the quote carries the `I` because the description is on a separate text line from the
`OE … 10 … I` row.

### 2.8 No `group` on any pin

The part has an A port and a B port plus three supplies, but `reference.md` allows `group` "only
when the part has separate units" (the `lm358_soic8` precedent: two *identical amplifiers*). The A
and B sides of a level translator are two views of one bidirectional channel set, not separate
amplifier units, and KiCad's symbol draws a single box. `group` is omitted everywhere, including
for the supplies. Pin order in the spec is ascending by pin number.

### 2.9 MPN `TXS0108EPW`

The task asks for the PW (TSSOP-20) option. The datasheet's orderable part is `TXS0108EPWR`
(tape-and-reel, p.26/27); `TXS0108EPW` is the package-level part number and is what KiCad's
official symbol uses, so the gold uses it.

## 3. Things in the datasheet that contradict themselves, or that are traps

1. **"Package size" on p.1 does not match the package drawing.** The Package Information table
   gives `PW (TSSOP, 20)` a package size of **6.50mm × 6.40mm** (length × width, "includes pins,
   where applicable"). But PW0020A on p.28 gives body length 6.4–6.6 (nom 6.5), body width
   **4.3–4.5** (nom 4.4) and a lead-tip-to-lead-tip span across the rows of 6.2–6.6. The
   6.50 × 6.40 pair therefore matches **body length × lead span**, not body length × body width, and
   the "4.4 mm" body width of the drawing is absent from the p.1 table. The drawing wins (it is the
   dimensioned drawing); the p.1 line is a summary table and is not quoted in the spec. Anyone
   cross-checking `body_width` against p.1 will get a false alarm here.
2. **`2X 5.85` (p.28) vs `(5.8)` (p.29)** — two different, easily confusable spans one page apart
   (lead row centrelines vs land pad row centres). Not a contradiction, but they must not be merged.
3. **The "Thermal Pad" row of Table 4-1 is a trap.** Table 4-1 is shared by PW, RGY and DGS and has
   a final `Thermal Pad` row with an **empty PIN column** and type `—`; its description says
   "For the RGY package, the exposed center thermal pad must be either be connected to Ground or
   left electrically opened." The PW package has **no** exposed pad. The gold therefore has
   `exposed_pad: false`, `pin_count: 20`, and **no** pin 21. (The RKS VQFN, Figure 4-4 on p.3, does
   show an "Exposed Center Pad" between pins 5 and 16 — also not the PW.)
4. **The pin-configuration page shows four packages** (Fig. 4-1 ZXY bumps, 4-2 NME, 4-3 PW/DGS,
   4-4 RKS VQFN) plus a separate ZXY/NME ball-assignment table. Fig. 4-3 is shared by PW and DGS.
   Both packages have the **same** 20-pin assignment, so the shared figure is safe here, but the
   ball table (rows D/C/B/A) and Fig. 4-4 (with the exposed centre pad) are not. All 20 pairings
   were confirmed on the rendered image of Fig. 4-3, not from the text layer, and independently
   against Table 4-1's `PIN PW, RGY, DGS` column.
5. **The "ZXY, NME" column of Table 4-1 is a second, different pin numbering.** Reading the wrong
   column gives 20 wrong numbers (e.g. `A1` is pin `1` for PW but ball `B1` for ZXY; `B1` is pin
   `20` for PW but ball `C1` for ZXY). The quotes in the spec carry all three columns so a human
   can see which column was used.
6. **Two `6.6` values on the outline** (the lead span max and the body length max) and two `4.5`-ish
   numbers interleaved with `0.19` in the text layer. The quotes were chosen to keep each value
   attached to its own callout's neighbours; the *assignment* of each was done on the rendered
   images, not the text.

## 4. Validation

```
kicad-partspec validate spec.gold.json --datasheet txs0108e.pdf   -> passed: true (0 failures, 5 status.inferred warnings)
kicad-partspec build spec.gold.json --out out --concise            -> passed: true, 0 failures, 5 warnings
                                                                          out/TXS0108EPW.kicad_sym
                                                                          out/partspec.pretty/TSSOP-20_4.4x6.5mm_P0.65mm.kicad_mod
```

Every `source.quote` was taken from `pdftotext -layout` output of the cited page and passed the
in-loop validator; no quote is off its page. The five warnings are all "this is `inferred`" — the
three supply pins (`power_in`), `standoff`, and `land_span` — and are intentional.
