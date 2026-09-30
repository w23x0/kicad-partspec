# Review — Nexperia 74HC595D, SOT109-1 (SO16)

Datasheet: `74HC595.pdf`, sha256 `fa24207e…b211a`, **Rev. 12 — 20 March 2024**
(cover page footer and Table 11 revision history, PDF page 19), 21 pages.
Source: <https://assets.nexperia.com/documents/data-sheet/74HC_HCT595.pdf>

Package page used: **page 15**, "Fig. 12. Package outline SOT109-1 (SO16)".
(The same datasheet also carries SOT403-1/TSSOP16 on p16, SOT763-1/DHVQFN16 on p17 and
SOT8016-1/DHXQFN16 on p18 — all ignored, only the SO16 D package was used.)

## 1. KiCad disagreements

Cross-checked against
`/usr/share/kicad/symbols/74xx.kicad_sym` (symbol `74HC595`, no `extends` — all 16 pins
are in the symbol itself) and
`/usr/share/kicad/footprints/Package_SO.pretty/SOIC-16_3.9x9.9mm_P1.27mm.kicad_mod`.

**Pin numbers: 16/16 identical. No disagreement on any pin number.**

| # | Item | Datasheet (p4/p5) | KiCad | Decision | Page |
|---|---|---|---|---|---|
| 1 | pin 1 name | `Q1` | `QB` | **Datasheet wins.** Nexperia names the outputs Q0–Q7; KiCad uses the TI alphabetic QA…QH convention. Not a disagreement about which pin carries a parallel output — only about spelling. | 4 (Fig. pinning) |
| 2 | pins 1–7, 15 names | `Q1`…`Q7`, `Q0` | `QB`,`QC`,`QD`,`QE`,`QF`,`QG`,`QH`,`QA` | **Datasheet wins**, same reason as #1. Ordering is identical, so the pin→output-index mapping is confirmed. | 4, 5 |
| 3 | pin 9 name | `Q7S` | `QH` (also the name it gives pin 7) | **Datasheet wins.** `Q7S` is the serial (shift-register cascade) output; KiCad's symbol merges the serial and parallel outputs onto the same letter and distinguishes them only by pin number. The two names denote different signals, so the datasheet's `Q7S` is the correct primary name. | 5 (Table 2) |
| 4 | pin 10 name | `MR` | `~{SRCLR}` | **Datasheet wins** (primary name is Nexperia's `MR`). KiCad's `~{SRCLR}` additionally encodes the active-LOW overbar, which the datasheet shows graphically over `MR` and states in words as "master reset (active LOW)". The `~` is lost in the PDF text layer, so it cannot be reproduced in a quote-verified name. | 4, 5 |
| 5 | pin 11 name | `SHCP` | `SRCLK` | **Datasheet wins.** | 5 |
| 6 | pin 12 name | `STCP` | `RCLK` | **Datasheet wins.** | 5 |
| 7 | pin 13 name | `OE` (overbarred, active LOW) | `~{OE}` | **Datasheet wins** on the name; same overbar caveat as #4. | 5 |
| 8 | pin 14 name | `DS` | `SER` | **Datasheet wins.** | 5 |
| 9 | pin 15 name | `Q0` | `QA` | **Datasheet wins**, same as #2. | 5 |
| 10 | pins 8, 16 type | "ground (0 V)", "supply voltage" | `power_in` | **Agree.** `power_in`, status `inferred` (no I/O column exists; the mapping is the reference's supply/ground rule). | 5 |
| 11 | pins 1–7, 15 type | Table 2 says only "parallel data output"; the part title, §1, the feature list and Table 3 all say the outputs are **3-state** and go to `Z` (high-impedance OFF-state) when `OE` is HIGH | `tri_state` | **Agree → `tri_state`.** Table 3 on p5 makes this explicit ("parallel outputs in high-impedance OFF-state"), so this is read from the datasheet, not guessed. | 5 |
| 12 | pin 9 type | "serial data output"; Table 3 never puts `Qn`/`Q7S` in the `Z` state — `OE` only gates the *parallel* outputs | `output` | **Agree → `output`** (deliberately *not* `tri_state`). | 5 |
| 13 | pins 10–14 type | "…input" in Table 2 | `input` | **Agree.** | 5 |
| 14 | package | body width 3.9 mm, SO16, SOT109-1, JEDEC MS-012 | `SOIC-16_3.9x9.9mm_P1.27mm` | **Agree.** | 15 |

Dimensions vs the KiCad footprint (pads are IPC-7351, so pad *size* is not comparable; pitch,
row spacing and body size are):

| Dimension | Datasheet (p15) | KiCad footprint | Decision |
|---|---|---|---|
| pitch | `e` nom 1.27 | 1.27 (pad 1 y=4.445 → pad 8 y=-4.445, 7 steps) | **Agree.** |
| body_length | `D` 9.8–10.0 (typ 9.9) | name says 9.9 | **Agree.** |
| body_width | `E` 3.8–4.0 (typ 3.9) | name says 3.9 | **Agree.** |
| overall_width | `H_E` 5.8–6.2 | courtyard half-span 2.475 → 4.95 + pad… (IPC, not the datasheet's `H_E`) | Not a disagreement: KiCad's span is a courtyard/pad figure from IPC-7351, the datasheet's `H_E` is lead tip to lead tip. No value carried into the gold. |
| pad size / land pattern | **absent — this datasheet has no example land pattern or board-layout drawing** | pad 1.95 × 0.6 | No datasheet value to compare; **no `land_*` dimension is in the gold.** `footprint.skipped` on build is the correct outcome (see §3). |

KiCad pads (1.95 × 0.6 at ±2.475/±4.445) are consistent with the datasheet's `e` 1.27, `D`
9.8–10.0 and `E` 3.8–4.0, so no dimension is contradicted by KiCad either.

## 2. Values that had to be interpreted

1. **`body_thickness` = A2, min 1.25** — status `inferred`. The drawing does not spell out
   "body thickness". Detail X on p15 shows A2 spanning from the body underside up to the top
   of the body, i.e. the moulded-body height without the standoff; A1 separately spans the
   seating plane to the body underside. That is the JEDEC MS-012 definition of A2/A1, and
   1.25 mm (0.049") is the MS-012 A2 minimum. The datasheet gives **only a minimum** for A2
   (no nom, no max), so only `min` is recorded.
2. **`standoff` = A1, 0.10–0.25** — read off detail X (seating plane to body underside).
   Treated as `extracted` because the dimension is unambiguous in the drawing and the values
   are the classic SOIC standoff range.
3. **`overall_width` = H_E, 5.8–6.2** — dual-row rule from `reference.md`: lead tip to lead
   tip *across* the rows. The drawing shows H_E spanning exactly the two lead tips. `extracted`.
4. **`body_length` = D (9.8–10.0) and `body_width` = E (3.8–4.0)** — dual-row rule: D runs
   along the pin rows (front view), E across them. `extracted`.
5. **`lead_length` = L** — the drawing gives `L` nom 1.05 and min 0.4 with **no maximum**.
   Recorded as `min` + `nom` (not min/max), which is what the table prints.
6. **`lead_width` = b_p (0.31–0.51)** and **`lead_thickness` = c (0.10–0.25)** — b_p is the
   lead width in the plan view, c is the lead material thickness in the side view. `extracted`.
7. **The 3-state outputs (`Q0`–`Q7`)** — `tri_state` rather than `output`. Datasheet support is
   the part title ("3-state"), §1 ("3-state outputs"), the feature "Storage register with
   3-state outputs", and Table 3's `Z` entries. No I/O column exists, so nothing is literally
   labelled `O`, but the tri-state behaviour is stated, so the type is `extracted` rather than
   `inferred`.
8. **`OE` and `MR` written without the active-LOW overbar** — the overline is drawn as vector
   graphics and the PDF text layer contains plain `OE` / `MR` (verified: the character
   sequence is `0x4f 0x45`, no combining overline). `reference.md` requires the name as printed
   *in a quote that is on the page*, so the bare letter form is used. KiCad's `~{OE}` /
   `~{SRCLR}` preserve the polarity, which the datasheet states in words instead
   ("active LOW"). **If the PartSpec format ever grows an overbar field, these two pins should
   be revisited** — as it stands the symbol loses the active-LOW indication.
9. **`VCC` (subscript CC in the artwork)** — the text layer flattens the subscript to `VCC`,
   which is also the KiCad name. Recorded as `VCC`.
10. **No `group`** — the part is a single unit, so the field is omitted per `reference.md`.

## 3. Deliberately left out

* **All `land_*` dimensions.** Sections 12 (Package outline, p15–18) are the *only* mechanical
  pages; there is no "recommended footprint", "board layout", "land pattern", "soldering" or
  "reflow" section anywhere in the 21 pages (grep for `board layout|land pattern|soldering|
  reflow|standoff` returns nothing in the whole document). Consequently the build reports
  `footprint.skipped` and only `out/74HC595D.kicad_sym` is produced. Per the skill, these
  numbers must not be taken from the package outline, and none were.
* **`L_p` (max 1.27), `A3` (nom 0.25), `v` (0.2), `w` (0.25), `y` (0.1), `q`, `θ` (0°–8°).**
  These are lead-toe geometry, the lead-forming/positioning tolerances and the surface angle.
  None of them corresponds to a `reference.md` dimension name, and several (`w`, `v`, `y`) are
  positional/seating tolerances rather than sizes. Omitted rather than guessed.
* **`exposed_pad: false`** — correct, the SO16 has none.

## 4. Contradictions inside the datasheet

* **The mm and inch columns of the Fig. 12 dimension table are not self-consistent for `L`.**
  `L` is listed as nom 1.05 / min 0.4 mm but as nom 0.041 / min 0.016 in — those agree
  (1.05 mm = 0.041 in, 0.4 mm = 0.0157 in ≈ 0.016 in), so this one is fine.
* **`A1` inch row.** mm max 0.25 / min 0.10 prints as 0.010 / 0.004 in, consistent.
* **The genuinely odd one: `A3`.** It is printed as a **nominal-only** 0.25 mm (0.01 in) in
  the middle row with **no max and no min**, whereas every other lead dimension in the table
  (A, A1, b_p, c, D, E, H_E, L) carries an explicit max and/or min. Taken at face value this
  makes A3 a *typical* value, not a limit. The datasheet offers no way to tell whether the
  min/max are simply missing or deliberately suppressed, so A3 was **omitted** rather than
  recorded as a nominal lead-foot height.
* **`c` (lead thickness) is quoted nominal-side heavy.** 0.10–0.25 mm is a wide band for a
  lead that is 0.31–0.51 mm wide, but it is what the table prints, and it matches the
  IPC/JEDEC SOIC lead-thickness range, so it is carried as-is.
* **No other contradiction found.** The pinning figure (p4) and Table 2 (p5) agree with each
  other and with the ordering table (p2) on every one of the 16 pins, and the SO16 outline on
  p15 is self-consistent with the "body width 3.9 mm" note on p2.

## 5. Coverage of the verification

* All **16 pins** were read from the text and the pairing was confirmed by eye on the rendered
  image of **page 4** (Fig. 6.1 pinning, D package / SOT109-1 (SO16) column) and **page 5**
  (Table 2 pin description). All 16 agree.
* All **10 dimensions** come from **page 15** (Fig. 12), read from `pdftotext -layout` and then
  confirmed on the rendered page, including two 400-dpi crops of the dimension table (to settle
  the `A3` vs `b_p` column alignment, which the text layer renders ambiguously) and two crops
  of detail X (to settle what `A1` and `A2` measure).
* One trap worth recording: the plain text layer of the Fig. 12 table appears to put `0.31` in
  the `A3` column of the min row. The rendered image shows it under `b_p`, which is what the
  gold uses (`lead_width` 0.31–0.51). A text-only extraction would have produced a wrong
  `lead_width`.
