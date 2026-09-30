# Review — INA219 (SOIC-8, package D) gold PartSpec

Datasheet: `ina219.pdf`, SHA-256 `58004eda854d07478e6fc6f4398c114f60a3bcf18d4877471c7c1a306d1fa1cb`
(verified against `source.txt`), revision **SBOS448G — August 2008 — revised December 2015** (Rev. G).

Every pin and every dimension was found in `pdftotext -layout` output and then confirmed on a
150 dpi (plus two 300 dpi crops) render of the cited page:

| Page | Contents | Used for |
|---|---|---|
| 3 | Pin Configuration (both DCN SOT-23 and **D SOIC** top views) + Pin Functions table | all 8 pins |
| 33 | PACKAGE OUTLINE `D0008A`, drawing 4214825/C 02/2019 | 7 outline dimensions |
| 34 | EXAMPLE BOARD LAYOUT / LAND PATTERN EXAMPLE `D0008A` | 3 `land_*` dimensions |

The pinout figure on page 3 shows two packages side by side, so the pin-number-to-name pairing
was taken from the **right-hand "D Package 8-Pin SOIC Top View"** and cross-checked against the
`SOIC` column of the Pin Functions table on the same page. The two agree exactly:

`1 A1`, `2 A0`, `3 SDA`, `4 SCL`, `5 VS`, `6 GND`, `7 IN–`, `8 IN+`

---

## 1. Disagreements with the official KiCad library

Cross-checked against `INA219AxD` in `/usr/share/kicad/symbols/Sensor_Energy.kicad_sym`
(no `extends`; all 8 pins are in the symbol itself) and
`/usr/share/kicad/footprints/Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod`.

**The generated symbol is identical to the KiCad symbol on all 8 pins** (number, name and electrical
type) — verified by parsing both files, not by eye:

| Pin | Generated | KiCad |
|---|---|---|
| 1 | A1 / input | A1 / input |
| 2 | A0 / input | A0 / input |
| 3 | SDA / bidirectional | SDA / bidirectional |
| 4 | SCL / input | SCL / input |
| 5 | VS / power_in | VS / power_in |
| 6 | GND / power_in | GND / power_in |
| 7 | IN- / input | IN- / input |
| 8 | IN+ / input | IN+ / input |

### Dimension / footprint disagreements

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| D1 | Land pad length | `.061` (**1.55 mm**), ref. | `1.95` mm pad size (IPC-7351) | **Datasheet wins** — gold `land_pad_length` = 1.55. KiCad's pad comes from the IPC-7351 nominal-density generator, which deliberately makes pads longer than the TI land pattern; this is the anticipated pad-SIZE difference, not an error. | 34 (`8X (.061 ) [1.55]`) |
| D2 | Land pad row spacing | `(.213)` (**5.4 mm**) centre-to-centre | pads at x = ±2.475 → **4.95 mm** | **Datasheet wins** — gold `land_span` = 5.4. Same IPC-7351-vs-TI-land-pattern cause as D1. | 34 (`(.213) [5.4]`) |
| D3 | Land pad width | `.024` (**0.6 mm**) | 0.6 mm | agree — no disagreement | 34 |
| D4 | Pitch | `.050` (**1.27 mm**) | 1.27 mm | agree | 33 / 34 |
| D5 | Body size | 4.81–5.00 × 3.81–3.98 mm (nom 4.9 × 3.9) | footprint name `3.9x4.9mm` | agree | 33 |
| D6 | Overall lead-tip width | 5.80–6.19 mm | KiCad stores no such value (its ±3.7 mm is the **courtyard**, 7.4 mm total, not the lead span) | not a disagreement | 33 |

Net: **2 disagreements (D1, D2), both resolved in favour of the datasheet**, and in both cases the
cause is the one the task statement anticipates — KiCad pads are IPC-7351 derived while `land_*`
values must come from the datasheet's example land pattern. The resulting generated footprint is
8 roundrect pads, 1.27 mm pitch, x = ±2.7, size 1.55 × 0.6.

### Non-dimension disagreement

| # | Item | Datasheet says | KiCad says | Decision | Page |
|---|---|---|---|---|---|
| D7 | Pin 7 name glyph | `IN–` (U+2013 en dash) | `IN-` (ASCII hyphen) | **KiCad glyph kept.** `reference.md` says "Use the ASCII hyphen (`IN1-`, `V-`)" for `name`; SKILL.md's "keep en dashes" rule is about *quotes*, not names. So `name` = `IN-` while the `source.quote` preserves the printed `IN–`. Note the `lm358_soic8` example gold stores `IN1–` with an en dash in `name`, so this is the one place where following `reference.md` and following the example file disagree. | 3 |

### Considered but *not* a disagreement

Page 6 has a section headed **`OPEN-DRAIN DIGITAL OUTPUTS (SDA)`** (7.5 Electrical Characteristics,
`Logic 0 output level`, `High-level output leakage current`), and page 4's Absolute Maximum Ratings
list "Open-drain digital output current 10 mA". That is a real statement about SDA's output driver,
but the Pin Functions table on page 3 prints SDA's I/O column as **`Digital I/O`**, and
`reference.md` maps "I/O, port pin, bidirectional" → `bidirectional`. SDA is not an output-only pin;
it is the bidirectional I²C data line whose *output stage* happens to be open-drain (as on every I²C
device). The gold therefore uses `bidirectional`, which is also what KiCad uses. Flagged here because
`open_collector` is the defensible alternative reading and a reviewer may want to overrule it.

---

## 2. Values I had to interpret

1. **Pin column order in the quotes (page 3).** The Pin Functions table has columns
   `NAME | SOT-23 | SOIC | I/O | DESCRIPTION`. I was asked for the SOIC (D) package, so in every pin
   quote the *second* number is the one recorded (e.g. `A1  8  1` → pin **1**). The header row
   `NAME SOT-23 SOIC` is on the same page; it is not part of each quote. The pairing was confirmed
   independently on the rendered D-package top view, which prints the numbers one-per-side.
2. **`IN–` quote is shorter than the others (page 3).** The text layer splits the IN– row across
   three lines (`Analog …description…` / `IN–            2              7` / `Input         measured
   from this pin to ground.`), so no single contiguous quote carries the row and its I/O cell. The
   quote is therefore just `IN–            2              7`. Per SKILL.md a short quote carrying the
   label and the value is the right escape here.
3. **`land_span` marked `inferred` (page 34).** `(.213) [5.4]` is printed without a label; I read it
   on the rendered image as the centre-to-centre distance between the two pad rows (the arrow spans
   pad-1 centreline to pad-5 centreline). That identification is an interpretation, hence `inferred`.
   Same status as the `lm358_soic8` gold for the same callout on the same drawing.
4. **`lead_length` `.016-.050 [0.41-1.27]` (page 33, DETAIL A).** Marked `extracted`: DETAIL A's arrow
   runs from the body edge to the lead tip at the seating plane, which I checked on the 300 dpi crop.
   Consistent with the `lm358_soic8` gold, which extracts the identical JEDEC MS-012 callout.
5. **Which axes `overall_width` / `body_length` / `body_width` measure.** Fixed by reading the
   top view and the bottom view on the render: the `.228-.244` arrow runs across the lead rows
   (→ `overall_width`), `.189-.197` runs along them (→ `body_length`), `.150-.157` is the width across
   between the rows (→ `body_width`). Same drawing and same convention as the `lm358_soic8` gold.
6. **`mpn` = `INA219AxD`.** The datasheet's own orderable SOIC-8 part numbers are `INA219AID` /
   `INA219AIDR` and `INA219BID` / `INA219BIDR` (page 29, PACKAGE OPTION ADDENDUM) — there is no bare
   "INA219" in SOIC. I used `INA219AxD`, TI's/KiCad's combined-grade notation for "INA219, accuracy
   grade A, SOIC-8", so the gold lines up 1:1 with the official KiCad symbol name. If the grader
   expects a literal orderable number, `INA219AID` is the substitution. (The `lm358_soic8` gold uses
   the bare `LM358` because LM358 is orderable without a package suffix; that is why the two differ.)
7. **`VS` name spelling.** The datasheet sets the S as a subscript (`V_S`); `pdftotext` and KiCad both
   yield `VS`. Used `VS`.
8. **No `group` field.** `reference.md` reserves `group` for parts with separate units. INA219 is a
   single device, so the field is omitted for all 8 pins (unlike the `lm358_soic8` gold, which uses
   `A` / `B` / `power` for a dual op-amp).

## 3. Dimensions deliberately left out

All on page 33, PACKAGE OUTLINE `D0008A`:

| Callout | What it appears to be | Why omitted |
|---|---|---|
| `.005-.010 TYP [0.13-0.25]` | lead thickness (side view, arrows straddle the flattened foot) | `evals/README.md` "Conventions" explicitly names the SOIC `.005-.010` value as an ambiguous callout to leave out rather than guess. Confirmed by 300 dpi crop; omitted on convention, not because it is unreadable. |
| `.004-.010 [0.11-0.25]` | standoff / gap, body underside to lead foot (DETAIL A) | same convention: the SOIC `.004-.010` value is named as ambiguous. |
| `.010 [0.25]` ⌖ C A B | lead seating-plane / coplanarity tolerance, referenced to datums C, A, B | no `reference.md` dimension name; it is a positional tolerance, not a size. |
| `.004 [0.1] C` | PIN 1 ID AREA offset to datum C | feature of the pin-1 marker, not a package size. |
| `2X .150 [3.81]` | row-to-row centre-to-centre span of pins 1 and 4 (= 3 × pitch, 3.81 mm) | no `reference.md` name covers the *outline* row span (`land_span` is defined as coming from the land pattern only); it is also redundant with the pitch. |
| `(.041) [1.04]`, `0°–8°`, `4X (0°–15°)`, `R.002 [0.05]`, `4X (0 -15 )` | detail-A reference length, foot angle, foot angles, pad corner radius | no matching dimension name / not a package size for the outline or the pad geometry the schema models. |

## 4. Datasheet self-contradictions

**None found.** Checks made:

- The page-3 SOIC top view and the page-3 Pin Functions `SOIC` column agree on all 8 pin numbers.
- SOT-23 and SOIC pinouts are the same part rotated/renumbered consistently, with no pin carrying a
  different name between the two columns.
- The `4214825/C 02/2019` outline (p. 33) and the `4214825/C 02/2019` land pattern (p. 34) use the
  same drawing number and the same `SOIC - 1.75 mm max height` title, and the land-pattern pitch
  `6X (.050) [1.27]` matches the outline pitch `6X .050 [1.27]`.
- The `SOIC (D) | 8` pin count in the page-29 PACKAGE OPTION ADDENDUM matches the D-package figure
  and `package.pin_count`.
- Minor, and *not* a contradiction of a value used here: page 29 carries a live-generated
  `5-Mar-2026` addendum date while the datasheet body is stamped `REVISED DECEMBER 2015`; and the
  drawing is stamped `02/2019`, later than the Rev. G date. Neither affects any extracted value.

---

## 5. Status flags

- 6 pins `extracted` (1 A1, 2 A0, 3 SDA, 4 SCL, 7 IN-, 8 IN+) — number/name from page 3, type read
  from the printed I/O column (`Analog Input`, `Analog Input`, `Digital I/O`, `Digital Input`,
  `Digital Input`, `Digital Input`).
- 2 pins `inferred` (5 VS, 6 GND) — `power_in` chosen through the supply/ground row of the reference
  table; the datasheet's I/O column says only `Analog` for both.
- 9 dimensions `extracted`, 1 `inferred` (`land_span`).
- Nothing marked `confirmed`.

## 6. Tool results

```
kicad-partspec validate spec.gold.json --datasheet ina219.pdf   ->  passed: true  (0 failures)
kicad-partspec build    spec.gold.json --out out --concise     ->  passed: true  (0 failures, 3 warnings)
```

The 3 warnings are all `status.inferred` (pins VS and GND, and `land_span`) — the deliberate honesty
flags, not defects. **Every quote passed on the first validation attempt**; no quote needed repair.
Files written: `out/INA219AxD.kicad_sym` and `out/partspec.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod`.
No `footprint.skipped` warning: the land pattern is complete, so the footprint was generated.