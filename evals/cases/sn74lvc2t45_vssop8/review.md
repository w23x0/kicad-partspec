# SN74LVC2T45DCUR (VSSOP-8, DCU0008A) — gold review

Datasheet: `sn74lvc2t45.pdf`, SHA-256 `f0dc4a7a46a5b2020117e8bec614aec33f4f15784a82ab73dc3fa5f91d5c86bc`,
`SCES516N – DECEMBER 2003 – REVISED JUNE 2024` (Rev. N). Pages cited below are PDF page indexes.

Package: the part is offered in three packages (DCT = SSOP-8, DCU = VSSOP-8, YZP = DSBGA-8). Only **DCU**
(`DCU0008A`, package outline on page 31, example land pattern on page 32, example stencil on page 33) is
used here. Everything on pages 25–30 (YZP, DCT) and 34 (YEP) is ignored.

## 1. Cross-check against the official KiCad library

The KiCad symbol `SN74LVC2T45DCUR` in `Logic_LevelTranslator.kicad_sym` does **not** `extends` a parent
symbol; all eight pins are in it. It carries `(property "Footprint" "Package_SO:VSSOP-8_2.3x2mm_P0.5mm")` —
note that the footprint named in the task brief, `VSSOP-8_3x3mm_P0.65mm`, is a *different* VSSOP-8 variant
(3 × 3 mm body, 0.65 mm pitch) and is **not** the footprint this symbol uses. Both were compared below.

### Pins — no disagreements

| Pin | Datasheet (page 2, Table 4-1 / Figure 4-1) | KiCad symbol | Verdict |
|---|---|---|---|
| 1 | VCCA, P | VCCA, `power_in`, 1 | agree |
| 2 | A1, I/O | A1, `bidirectional`, 2 | agree |
| 3 | A2, I/O | A2, `bidirectional`, 3 | agree |
| 4 | GND, G | GND, `power_in`, 4 | agree |
| 5 | DIR, I | DIR, `input`, 5 | agree |
| 6 | B2, I/O | B2, `bidirectional`, 6 | agree |
| 7 | B1, I/O | B1, `bidirectional`, 7 | agree |
| 8 | VCCB, P | VCCB, `power_in`, 8 | agree |

The pinout figure (Figure 4-1) and Table 4-1 agree with each other, so no figure-versus-table decision was
needed; the figure was still checked on the rendered page (page 2) for the pin-number-to-name pairing.

### Dimensions — disagreements

| Item | Datasheet | KiCad | Decision | Page |
|---|---|---|---|---|
| `pitch` | **0.5 mm** (boxed basic, `6X 0.5`; land pattern `6X (0.5)`) | `VSSOP-8_3x3mm_P0.65mm`: **0.65 mm** (pads at y ±0.325, ±0.975) | **Datasheet wins.** The task's named footprint is the 0.65 mm-pitch 3 × 3 mm variant; this DCU drawing is a 0.5 mm-pitch, ~2 × 2.3 mm part. Confirmed three ways: the boxed callout, the land-pattern callout, and the drawn geometry (pin pitch measured 0.50 mm at the page's own scale). | 31, 32 |
| `pitch` | 0.5 mm | `VSSOP-8_2.3x2mm_P0.5mm` (the footprint the symbol actually uses): 0.5 mm | agree | 32 |
| body size | **1.9–2.1 × 2.2–2.4 mm** (`2.1/1.9` along the pin rows, `2.4/2.2` across) | 3 × 3 mm `VSSOP-8_3x3mm_P0.65mm`; 2.3 × 2.0 mm `VSSOP-8_2.3x2mm_P0.5mm` | **Datasheet wins** against the 3 × 3 footprint (wrong variant); the 2.3 × 2.0 mm footprint matches the gold's `body_width` 2.2–2.4 and `body_length` 1.9–2.1. | 31 |
| `land_span` | **(3.1) mm**, pad-row centre to centre (`(3.1)`) | 3 × 3 variant: pads at x = ±2.1125 → **4.225 mm**; 2.3 × 2 mm variant: x = ±1.4 → **2.8 mm** | **Datasheet wins.** The IPC-7351-generated KiCad pads sit inboard of TI's land pattern (2.8 vs 3.1). The generated gold footprint puts the pads at ±1.55, exactly TI's land pattern. | 32 |
| pad size | **0.85 × 0.30 mm** (`8X (0.85)`, `8X (0.3)`) | 1.625 × 0.5 mm (3 × 3) / 1.25 × 0.35 mm (2.3 × 2) | **Not a disagreement.** KiCad pads come from IPC-7351 and are legitimately larger; the datasheet land values were used. | 32 |
| pad count / pin-1 corner | 8 pads, pin 1 top-left, 1–4 down the left, 8–5 down the right | 8 pads, pin 1 at (−x, −y), 1–4 one row, 5–8 the other | agree | 31, 32 |

Count: **3 substantive KiCad disagreements** (pitch, body size, land span / pad-row spacing), all against the
`VSSOP-8_3x3mm_P0.65mm` footprint named in the brief, all decided for the datasheet on pages 31/32. Against
the footprint the KiCad symbol actually uses (`VSSOP-8_2.3x2mm_P0.5mm`) there is **no** disagreement in pitch,
pad count or body size; only the pad-row spacing differs, decided for the datasheet.

## 2. Values that had to be interpreted

1. **Which outline dimension is which.** The pin rows run vertically (1–4 on the left edge, 8–5 on the right
   edge), so "across the rows" is the horizontal direction of the top view. On the rendered page 31 at
   300 dpi the drawing scale works out at ~235 px/mm, and: the `3.2 / 3.0 TYP` callout spans 730 px between
   the lead tips → `overall_width` 3.0–3.2; `2.4 / 2.2` spans 545 px between the body edges → `body_width`
   2.2–2.4; `2.1 / 1.9` spans 453 px between the body edges along the rows → `body_length` 1.9–2.1. The three
   numbers are mutually consistent (2.32 mm and 1.93 mm measured against the stated ranges), which is what
   fixed the assignment.
2. **`standoff` = 0.0–0.1 mm, `inferred`.** The `0.1 / 0.0` callout in DETAIL A is the only vertical gap at the
   bottom of the lead. It is measured from the seating plane up to the dashed 0.12 gage plane, so it is a
   standoff, not a lead thickness — the lead thickness is printed separately as `(0.13) TYP` in the front
   view. Marked `inferred` because deciding that required reading the two planes of Detail A at 600 dpi; the
   drawing itself never names it A1.
3. **`lead_length` = 0.20–0.35 mm.** The `0.35 / 0.20` callout in DETAIL A is horizontal, from the body edge
   to the lead toe, i.e. the foot — not the body-to-tip length. Kept `extracted`; the arrows were unambiguous
   at 300/600 dpi. (Nexperia `Lp` / ST `L` equivalent.)
4. **`lead_thickness` = 0.13 mm.** `(0.13) TYP` in the front view; a parenthesised reference value, recorded
   as `nom` per the conventions.
5. **`pitch` = 0.5 mm, `nom`.** A boxed basic dimension with one printed value and no tolerance.
6. **`land_span` = 3.1 mm, `inferred`.** `(3.1)` is in parentheses (a reference value) and the extension lines
   land on the pad centrelines, so it is the centre-to-centre distance between opposite pad rows. Marked
   `inferred` following the `lm358_soic8` precedent.
7. **Pin types `bidirectional`, not `tri_state`, for A1/A2/B1/B2.** The features list says the ports go
   high-impedance under VCC isolation (either VCC at GND) and Ioff partial-power-down, which would argue for
   `tri_state` under the skill's "a pin the part can put in Z is tri_state" rule. The datasheet's own TYPE
   column prints `I/O`, which maps directly to `bidirectional`; KiCad's symbol says `bidirectional`; and the
   sibling level-translator gold (`txs0108e_tssop20`, same Hi-Z behaviour) types all 20 pins `bidirectional`.
   The Hi-Z state here is a power condition, not the pin's normal function, so `bidirectional` was kept.
8. **No `group` on any pin.** reference.md states that the A and B ports of a level translator are not units
   and stay ungrouped. The supply pins get no `power` group here (matching `txs0108e_tssop20` and
   `ads1115_vssop10`): this datasheet prints no supply block of its own, and grouping a lone supply or ground
   pin is optional.
9. **`mpn` = `SN74LVC2T45DCUR`**, the orderable suffix that names this VSSOP-8 package (the bare
   `SN74LVC2T45` is offered in three packages), following the `ADS1115IDGS` precedent.
10. **No `alt_names`.** VCCA, VCCB, GND and DIR each have a single printed function; the two-sided function
    of A1/A2/B1/B2 is not an alternate function.
11. **Quotes that straddle neighbouring drawing tokens.** TI's drawing text layer interleaves unrelated labels,
    so some quotes carry a neighbour: `3.2 TYP C 3.0` (the `C` is a datum letter), `2.1 1.5 1.9 NOTE 3`
    (the `1.5` is the pin 5–8 centreline span), `0.1 0 -6 0.35 0.0` (the `0 -6` is the lead coplanarity
    angle). This is the page's own token order, which is what the skill prescribes; all quotes were confirmed
    against `pdftotext -layout` output.
12. **Values deliberately left out:** the `2X 1.5` pin-centreline span (reference.md: a lead centre-to-centre
    span is not recorded), the `0.08 Ⓜ C A B` positional tolerance, the `0°–6°` coplanarity angle, the boxed
    `0.12` gage-plane height (a basic reference, not one of the dimension names), and the solder-mask
    details on page 32. No `body_thickness`: the drawing gives no separate body height.

## 3. Places where the datasheet is inconsistent or easy to misread

1. **The cover "PACKAGE SIZE" mixes body and overall dimensions.** Page 1 gives `DCU (VSSOP, 8) 2mm × 3.1mm`.
   2 mm is the *body* length (1.9–2.1 on page 31) and 3.1 mm is the *tip-to-tip* width across the rows
   (3.0–3.2 on page 31) — the body width is only 2.2–2.4. Read as body × body it would contradict the outline
   drawing. The same shorthand appears in the DCT row (`2.95mm × 4mm` = 3.0 body length × 4.0 overall width on
   page 28) and the YZP row (`1.5mm × 0.5mm` = ball pitch), so it is house style rather than a wrong number.
2. **Pin names A1/A2/B1/B2 mean two different things.** Table 4-2 on page 3 uses them as the *ball names* of
   the YZP DSBGA (balls A1, A2, B1, B2 alongside C1/C2 and D1/D2), while Table 4-1 on page 2 uses them as
   pin *names* of the DCT/DCU packages. The gold uses Table 4-1; quoting the wrong table would give the
   right name with no number to pair it to.
3. **Figure 4-1 is shared by two different packages.** Its caption reads "DCT or DCU Package", but DCT0008A
   (page 28) is a 0.65 mm-pitch SSOP-8 and DCU0008A (page 31) is a 0.5 mm-pitch VSSOP-8 of a different body
   size. The pinout is identical for both, so the figure is not wrong, but its dimensions must not be read as
   applying to both.
4. **Note 3 applies to both body dimensions** (`2.1 / 1.9` and `2.4 / 2.2`): neither includes mold flash,
   protrusions or gate burrs, which may add up to 0.15 mm per side. A rendered pad layout taken from the
   outline alone would therefore be up to 0.3 mm per side too large.

## 4. Verification

- `kicad-partspec validate spec.gold.json --datasheet sn74lvc2t45.pdf` → `passed: true`, 5 warnings, all of
  them `status.inferred` (pins 1/4/8, `standoff`, `land_span`). No failures.
- `kicad-partspec build spec.gold.json --out out --concise` → `passed: true`, 0 failures, 5 warnings,
  producing `out/SN74LVC2T45DCUR.kicad_sym` and
  `out/partspec.pretty/VSSOP-8_2.3x2.0mm_P0.5mm.kicad_mod` (8 pads, 0.85 × 0.3 mm, pitch 0.5, rows at
  ±1.55 mm — the datasheet land pattern exactly).
- Quote check re-run through the repo's own checker (`kicad_partspec.verify.quotes.check_quotes` against
  `pdftotext -layout` page text): no findings.
- Every pin and every dimension was read on a rendered page image (pages 2, 31, 32 at 150–600 dpi), not from
  the text layer alone.
