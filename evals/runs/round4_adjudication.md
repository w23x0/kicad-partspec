# Adjudication — extraction round r4

Every disagreement in `score_output.txt` was re-decided against the datasheet PDF. Pages are **PDF page
indexes** (starting at 1). Values are millimetres. Rules applied: `skills/partspec/SKILL.md` and
`skills/partspec/reference.md`.

One row per distinct item; the run1/run2 columns show what each run put there (`—` = field absent).

This file is the round's verbatim record. Two items it leaves open were settled when the round's
golds were imported (`w/r4fix`, merged into `next`), and the settlements are recorded where the
reposability now lives: the ne555 `standoff` (item 7 below) is recorded in the gold — page 30
re-rendered at 600 dpi shows the `.004-.010 [0.11-0.25]` extension lines span body underside to
seating plane — see the Conventions section of `evals/README.md`; and the ULN2003A `COM` group
(item 1 below) stays ungrouped while `E` takes `power`, on the datasheet's own power-supply text
(§8.4 "This device does not need a power supply", §7.4.2 COM may float) — see the supply carve-out
in `skills/partspec/reference.md`.

---

## ne555_soic8 — TI NE555, D0008A (SOIC-8)

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| `lead_length` (missing) | — | min 0.41 / max 1.27 | min 0.41 / max 1.27 | **GOLD** | 30 | `.016-.050 [0.41-1.27]` in DETAIL A runs lead tip → start of bend = foot length; run1 dropped a dimension the sheet plainly gives. |
| `overall_width` | nom 3.81 | min 5.8 / max 6.19 | min 5.8 / max 6.19 | **GOLD** | 30 | `.228-.244 TYP [5.80-6.19]` spans lead tip to lead tip across the rows; 3.81 is the `2X .150 [3.81]` lead centreline span, which reference.md says not to record. |
| `lead_thickness` (extra) | nom 0.25 | min 0.13 / max 0.25 | — | **RUN** | 30 | Front view: `.005-.010 TYP [0.13-0.25]` with arrows across the lead toe is the lead thickness. Run2 right; gold should carry it (range → min/max per reference.md). |
| `lead_width` (run2) | min 0.31 / max 0.51 | min 0.11 / max 0.25 | min 0.31 / max 0.51 | **GOLD** | 30 | `8X .012-.020 [0.31-0.51]` is the lead width; 0.11–0.25 is the DETAIL A standoff run2 then also recorded. |
| `standoff` (extra) | min 0.13 / max 0.25 | nom 0.25 | — | **NEITHER** | 30 | Correct value is `.004-.010 [0.11-0.25]` → min 0.11 / max 0.25 (DETAIL A, body underside → seating plane). Gold omits it; run1 reused the lead thickness, run2 kept only the upper limit as a nominal. |

---

## 24lc256_soic8 — Microchip 24LC256 (SOIC-8)

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| pin 4 `group` | `power` | `power` | — | **GOLD** | 5 | reference.md allows `group` "only when the datasheet shows repeated, identical functional blocks"; an EEPROM is one block, so `group` must be omitted. |
| pin 5 `electrical_type` | `open_collector` | `open_collector` | `bidirectional` | **GOLD** | 5 | §2.2: "This is a **bidirectional** pin used to transfer addresses and data into and out of the device. It is an open drain terminal." The open-drain rule in reference.md applies to *outputs*; SDA is not one. |
| pin 8 `group` | `power` | `power` | — | **GOLD** | 5 | Same as pin 4. |

---

## ina226_vssop10 — TI INA226, DGS0010A (VSSOP-10)

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| pin 6 (`VS`) `group` | `power` | `power` | — | **GOLD** | 4 | Table 4-1 gives ten distinct single-instance pins; no repeated identical block, so no `group`. |
| pin 7 (`GND`) `group` | `power` | `power` | — | **GOLD** | 4 | As above. |
| `standoff` | nom 0.25 | nom 0.1 | min 0.05 / max 0.15 | **GOLD** | 38 | DETAIL A `0.15` over `0.05` spans body underside → seating plane. 0.25 is the **boxed BASIC** gage-plane offset; `0.1` occurs only inside GD&T frames, never as a linear dimension. |

---

## pca9306_vssop8 — TI PCA9306, DCU0008A (VSSOP-8)

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| pin 3 (`SCL1`) type | `open_collector` | `bidirectional` | `bidirectional` | **GOLD** | 4 | Table 5-1 TYPE column prints `I/O` → `bidirectional`. The datasheet's "Open-drain I2C I/O ports" (p.1) describes the external bus; "open-collector"/"open collector" appear nowhere in it. |
| pin 4 (`SDA1`) type | `open_collector` | `bidirectional` | `bidirectional` | **GOLD** | 4 | As pin 3. |
| pin 5 (`SDA2`) type | `open_collector` | `bidirectional` | `bidirectional` | **GOLD** | 4 | As pin 3. |
| pin 6 (`SCL2`) type | `open_collector` | `bidirectional` | `bidirectional` | **GOLD** | 4 | As pin 3. |
| `lead_thickness` (missing in run1) | — | nom 0.13 | nom 0.13 | **GOLD** | 31 | `(0.13) TYP` in the side view has arrows across the lead cross-section at the toe — unambiguously the lead thickness. (Parenthesised = reference per Note 1; value is still a stated one, marked `inferred`.) |

---

## tca9548a_tssop24 — TI TCA9548A, PW0024A (TSSOP-24)

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| pins 4,5 `group` | — | `CH0` | — | **RUN** | 3, 13 | Pins 4/5 are `SD0`/`SC0`; §7.2 draws eight identical switches and p.16 says "eight channels … Any individual downstream channel can be selected". Eight repeated identical blocks → `group` is required. |
| pins 6,7 `group` | — | `CH1` | — | **RUN** | 3, 13 | `SD1`/`SC1`, channel 1. |
| pins 8,9 `group` | — | `CH2` | — | **RUN** | 3, 13 | `SD2`/`SC2`, channel 2. |
| pins 10,11 `group` | — | `CH3` | — | **RUN** | 3, 13 | `SD3`/`SC3`, channel 3. |
| pin 12 (`GND`) `group` | — | `power` | — | **RUN** | 3 | reference.md names the supply pins as the `power` key, and this part does have repeated units. |
| pins 13,14 `group` | — | `CH4` | — | **RUN** | 3, 13 | `SD4`/`SC4`, channel 4. |
| pins 15,16 `group` | — | `CH5` | — | **RUN** | 3, 13 | `SD5`/`SC5`, channel 5. |
| pins 17,18 `group` | — | `CH6` | — | **RUN** | 3, 13 | `SD6`/`SC6`, channel 6. |
| pins 19,20 `group` | — | `CH7` | — | **RUN** | 3, 13 | `SD7`/`SC7`, channel 7. |
| pin 24 (`VCC`) `group` | — | `power` | — | **RUN** | 3 | As pin 12. |
| `body_length` | min 6.2 / max 6.6 | min 7.7 / max 7.9 | min 7.7 / max 7.9 | **GOLD** | 36 | `7.9 / 7.7 NOTE 3` runs pin 1 → pin 12 along the rows (moulded body); run1 swapped it with the across-rows span. |
| `lead_length` (missing in run1) | — | min 0.5 / max 0.75 | min 0.5 / max 0.75 | **GOLD** | 36 | DETAIL A `0.75 / 0.50` spans lead tip → start of bend. |
| `lead_thickness` | min 0.05 / max 0.15 | — | min 0.05 / max 0.15 | **NEITHER** | 36 | The `0.15 / 0.05` callout is **the standoff**, not the lead thickness (see next row). The sheet's only thickness callout is `(0.15) TYP` in the front view, parenthesised = reference, so it must be omitted. Correct: no `lead_thickness` at all. |
| `standoff` (extra in both runs) | min 0.5 / max 0.75 | min 0.05 / max 0.15 | — | **NEITHER** | 36 | Correct value is `0.15 / 0.05` → min 0.05 / max 0.15, drawn in DETAIL A exactly as the standoff on DCU0008A (`0.1 / 0.0`) and PW0016A. Gold omits it; run1 put the lead length there. |
| `overall_width` | min 7.7 / max 7.9 | min 6.2 / nom 6.6 | min 6.2 / max 6.6 | **GOLD** | 36 | `6.6` / `6.2 TYP` spans lead tip to lead tip across the rows; a stacked pair on this sheet is max-over-min (cf. `7.9/7.7`, `4.5/4.3`, `0.30/0.19`), so min/max, and 6.4 is printed nowhere. |

---

## uln2003a_tssop16 — TI ULN2003A, PW0016A (TSSOP-16)

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| pin 1 (`1B`) `group` | `1` | `1` | — | **RUN** | 1, 3, 14 | "Each consists of **seven NPN Darlington pairs**" (p.1); §7.1 p.14 "seven high-voltage, high-current NPN Darlington transistor pairs … Each channel". Seven repeated identical blocks → `group` required, keyed by the datasheet's own channel numbers. |
| pin 2 (`2B`) `group` | `2` | `2` | — | **RUN** | 3 | Channel 2. |
| pin 3 (`3B`) `group` | `3` | `3` | — | **RUN** | 3 | Channel 3. |
| pin 4 (`4B`) `group` | `4` | `4` | — | **RUN** | 3 | Channel 4. |
| pin 5 (`5B`) `group` | `5` | `5` | — | **RUN** | 3 | Channel 5. |
| pin 6 (`6B`) `group` | `6` | `6` | — | **RUN** | 3 | Channel 6. |
| pin 7 (`7B`) `group` | `7` | `7` | — | **RUN** | 3 | Channel 7. |
| pin 8 (`E`) `group` | `power` | `power` | — | **RUN** | 3 | "Common emitter shared by all channels" — the supply/ground key reference.md names explicitly. |
| pin 9 (`COM`) `group` | `power` | `power` | — | **RUN** | 3 | Common cathode node, the device's other supply rail. |
| pins 16,15,14,13,12,11,10 (`1C`…`7C`) `group` | `1`…`7` | `1`…`7` | — | **RUN** ×7 | 3 | `1C`…`7C` are the output side of the same seven channels; the two sides of one unit share a key (that is what reference.md's "the two sides of one function are not units" forbids splitting). |
| `overall_width` | min 6.2 / max 6.6 | min 6.2 / max 6.6 | nom 6.2 / max 6.6 | **RUN** | 38 | `6.6` over `6.2 TYP` is the same top=max/bottom=min stacked pair used for `5.1/4.9`, `4.5/4.3`, `0.30/0.17`, `0.75/0.50`, `0.15/0.05` on this sheet. A nominal equal to the lower limit of its own range is not a reading any convention supports (the midpoint 6.4 is printed nowhere). |
| `lead_width` | nom 0.17 | min 0.17 / max 0.30 | min 0.17 / max 0.30 | **GOLD** | 38 | `16X 0.30 / 0.17` spans one lead edge to edge; run1 dropped the upper limit. |
| `standoff` | nom 0.05 | min 0.05 / max 0.15 | min 0.05 / max 0.15 | **GOLD** | 38 | DETAIL A `0.15 / 0.05`, gauge plane → lead-foot underside; run1 kept only the lower limit. |
| `lead_thickness` (extra) | nom 0.3 | nom 0.15 | — | **GOLD** | 38 | The sheet's thickness callout is `(0.15) TYP` — parenthesised, so reference-only per Note 1 and not usable for a package dimension. 0.3 is not a thickness (it is the lead-width upper limit). Omitting it is correct. |

---

## tps5430_soic8 — TI TPS5430, DDA0008B (SOIC-8 PowerPAD)

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| pin 9 `name` | `DAP` | `EP` | `DAP` | **GOLD** | 3 | Table 4-1's last row and Figure 4-1 both print `DAP`; TI's revision history records "Changed 'PwPd' to 'DAP' on the TPS5430DDA package drawing". `name` is "the primary function as printed"; `EP` is the generic convention reference.md mentions, not this datasheet's word. |
| `ep_size` (missing in run1) | — | min 2.0 / max 2.6 | min 2.11 / max 2.71 | **GOLD** | 38 | Bottom view of DDA0008B prints `2.71` over `2.11` across the pad (and `3.4`/`2.8` on the other axis). 2.0–2.6 belongs to the superseded `DDA0008J` drawing on page 35, not the page in use. |
| `land_ep_size` | nom 2.95 | nom 2.95 | nom 2.71 | **GOLD** | 39 | `(2.71)`/`(3.4)` dimension the solid green rectangle labelled "SOLDER MASK DEFINED PAD" and match the package pad's maxima. `(2.95)`/`(4.9)` (NOTE 9, "Size of metal pad may vary due to creepage requirement") dimension the dashed "METAL COVERED BY SOLDER MASK" outline. |
| `land_span` | nom 5.4 | nom 4.9 | nom 5.4 | **GOLD** | 39 | `(5.4)` runs centreline-to-centreline between the two pad rows. `(4.9)` is a *vertical* dimension on the pad-9 mask opening. |
| `overall_width` | min 5.8 / max 6.2 | min 5.8 / max 6.2 | nom 5.8 / max 6.2 | **RUN** | 38 | `6.2` over `5.8` spans lead tip to lead tip across the rows, and is one of the sheet's plain stacked max/min pairs like `5.0/4.8`, `4.0/3.8`, `0.51/0.31`, `2.71/2.11`. Correct: min 5.8, max 6.2. (The gold review also mis-states the sheet: it reads `6.2` over `5.8 TYP`, but the render shows `TYP` on 6.2's line — either way 5.8 is the lower limit, not a nominal.) |

---

# Gold corrections

Everything below is a change to a gold file. **No gold file was edited.**

### `gold/uln2003a_tssop16/spec.gold.json`

1. **Add `group` to all 16 pins.** The part is seven identical Darlington channels and the datasheet names them
   numerically, so the runs' keys are the datasheet's own:
   - pins 1–7 (`1B`…`7B`) → `"1"`, `"2"`, … `"7"`
   - pins 16, 15, 14, 13, 12, 11, 10 (`1C`…`7C`) → `"1"`, `"2"`, … `"7"`
   - pins 8 (`E`) and 9 (`COM`) → `"power"`
   Evidence: p.1 "Each consists of seven NPN Darlington pairs"; p.14 §7.1 "seven high-voltage, high-current
   NPN Darlington transistor pairs … Each channel"; p.15 §7.3 "Each channel of the ULN2003A device consists of
   Darlington connected NPN transistors". The gold review's stated reason (no unit *letters* printed) is not a
   requirement in SKILL.md/reference.md — reference.md offers `"A"`,`"B"` only as examples of keys.
2. **`overall_width`: `nom 6.2 / max 6.6` → `min 6.2 / max 6.6`** (page 38, quote `6.6 C TYP A 6.2`).

### `gold/tca9548a_tssop24/spec.gold.json`

3. **Add `group` to 19 pins** — pins 4/5 → `"CH0"`, 6/7 → `"CH1"`, 8/9 → `"CH2"`, 10/11 → `"CH3"`, 13/14 →
   `"CH4"`, 15/16 → `"CH5"`, 17/18 → `"CH6"`, 19/20 → `"CH7"`; pins 12 (`GND`) and 24 (`VCC`) → `"power"`.
   Evidence: p.13 §7.2 functional block diagram shows eight identical switches; p.16 "The TCA9548A is an 8-channel,
   bidirectional translating I2C switch … directed to eight channels of target devices, SC0/SD0-SC7/SD7. Any
   individual downstream channel can be selected as well as any combination of the eight channels"; p.1 "one sensor
   can be connected at each channel: 0-7".
4. **Rename the `lead_thickness` dimension to `standoff`** (values unchanged: min 0.05 / max 0.15, quote
   `0.15 0.05`, page 36). DETAIL A's `0.15 / 0.05` measures gauge/seating plane → body underside; the same callout
   is the standoff on DCU0008A (`0.1 / 0.0`, PCA9306) and PW0016A (ULN2003A). The sheet's only lead-thickness
   callout is `(0.15) TYP` in the front view, parenthesised = reference only (Note 1), so **no `lead_thickness`
   entry should remain**. Note this makes the two TSSOP golds consistent — the ULN2003A gold already has it this way.

### `gold/tps5430_soic8/spec.gold.json`

5. **`overall_width`: `nom 5.8 / max 6.2` → `min 5.8 / max 6.2`** (page 38, quote `6.2 TYP SEATING PLANE 5.8`).

### `gold/ne555_soic8/spec.gold.json`

6. **Add `lead_thickness` min 0.13 / max 0.25**, page 30, quote `.005-.010 TYP [0.13-0.25]` — front view, arrows
   across the lead toe. Higher confidence: the callout is unambiguous at 150 dpi.
7. **Add `standoff` min 0.11 / max 0.25**, page 30, quote `.004-.010 [0.11-0.25]` — DETAIL A, body underside to
   seating plane. **Lower confidence:** the gold's omission follows `evals/README.md`'s standing convention that
   the SOIC `.004-.010` / `.005-.010` callouts are ambiguous and are left out. At 600 dpi this one does resolve
   cleanly (dash-dot extension line at the body underside → extension line at the seating plane), so under
   SKILL.md/reference.md alone it should be recorded; a human should decide whether to override the repo convention.

---

## Notes on the round

- The scorer marks `usable=no` for **both** runs of `uln2003a_tssop16` and for `tca9548a_tssop24_run2`. In
  `uln2003a_tssop16` every one of those differences is a gold error, so the score understates both runs; in
  `tca9548a_tssop24` the group rows are gold errors while the dimension rows are genuine run errors.
- Three golds share the same class of defect: two (`uln2003a`, `tca9548a`) treat a part built from repeated
  identical blocks as having no units because the datasheet labels the units numerically rather than with
  letters; two (`uln2003a`, `tps5430`) read a stacked `max / min TYP` pair as `nom / max`. The TCA9548A gold
  already uses `min`/`max` for the identical `6.6 / 6.2 TYP` callout, so the three golds disagree with each other.
- No `BOTH` verdicts were needed: in every case the rules plus the page pick a single answer.

## Counts

Counted as **one item per contested pin or per contested dimension** (the `tca9548a` and `uln2003a`
tables print several identical pins on one line, but each is counted separately).

| verdict | count |
|---|---|
| GOLD | 24 |
| RUN | 37 |
| BOTH | 0 |
| NEITHER | 3 |
| **total rows** | **64** |

By case: ne555 5 (GOLD 3, RUN 1, NEITHER 1) · 24lc256 3 (GOLD 3) · ina226 3 (GOLD 3) · pca9306 5 (GOLD 5) ·
tca9548a 23 (GOLD 3, RUN 18, NEITHER 2) · uln2003a 20 (GOLD 3, RUN 17) · tps5430 5 (GOLD 4, RUN 1).