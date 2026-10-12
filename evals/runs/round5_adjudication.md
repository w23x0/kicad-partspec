# Round r5 — adjudication

Five cases, two runs each. Every disagreement between a run and the gold was decided against the
datasheet and the rules the runs were given (`skills/partspec/SKILL.md` + `reference.md`), never by what
seemed sensible. Per-case sections below are the adjudicators' files verbatim; the merged Counts and
merged Gold corrections are at the end.

Verdicts: **GOLD** = gold right, run wrong · **RUN** = run right, gold wrong · **BOTH** = datasheet or
rules genuinely permit both · **NEITHER** = both wrong.


# Adjudication: ads1015_vssop10

Package drawing **DGS0010A** (p.47), land pattern p.48, Table 5-1 / Figure 5-2 p.3.

## Findings

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| dims.body_length | min 4.75 / max 5.05 | min 2.9 / max 3.1 | min 2.9 / max 3.1 | GOLD | 47 | Top view prints the body along the pin rows as `3.1 / 2.9 NOTE 3` against datum **A**; the `5.05 / 4.75 TYP` pair it took instead is the tip-to-tip arrow (see overall_width). |
| dims.overall_width | min 3.8 / max 4.4 | min 4.75 / max 5.05 | min 4.75 / max 5.05 | GOLD | 47 | The `5.05 / 4.75 TYP` arrow at the top of the top view runs from the left lead tips to the right lead tips (outside the `2.9–3.1` body), i.e. the largest across-the-rows span; run1's 3.8/4.4 comes from DETAIL A's `0.7 / 0.15 / 0 -8 / 0.05 / 0.4`, which measures no across-row span at all. |
| dims.lead_length | nom 0.25 (`0.25 GAGE PLANE`) | min 0.4 / max 0.7 | min 0.4 / max 0.7 | GOLD | 47 | DETAIL A's horizontal arrow runs toe → start of the bend, the flat foot on the board: `0.7 / 0.4`; `0.25 GAGE PLANE` is a boxed reference locating the gage plane, not a lead length. |
| dims.standoff | min 0.05 / max 0.15 | nom 0.25 (`0.25 GAGE PLANE`) | min 0.05 / max 0.15 | GOLD | 47 | DETAIL A's `0.15 / 0.05` arrow spans body underside → seating plane (datum C) — the standoff; the gage-plane value is a different dimension and belongs to none of the named fields. |
| pin 2 `alt_names` | `["RDY"]` | absent (empty) | `[]` | GOLD | 3 | The datasheet prints the whole pin name as one token, `ALERT/RDY` (Table 5-1 NAME column and Figure 5-2); there is no separately-printed second name left to move into `alt_names`. |
| pin 3 `group` | `"power"` | absent (none) | none | BOTH | 3 | reference.md gates `group` on "repeated, **identical** functional blocks" — GND and VDD are not identical (gold's reading) — but the same bullet explicitly names "the supply pins `power`" as a permitted group value, which is exactly this pin pair (run1's reading). Both are rule-compliant; neither changes the generated symbol's electrical content. |
| pin 8 `group` | `"power"` | absent (none) | none | BOTH | 3 | Same rule tension as pin 3, applied to VDD: the enumerated `power` value sanctions it; the "identical blocks" precondition is not literally met by one GND + one VDD. |
| pins 4–7 `status` | extracted (agrees with gold) | inferred | extracted | GOLD | 3 | Table 5-1 TYPE column prints `Analog input` for AIN0–AIN3, i.e. a direction **is** printed, so reference.md's "status `inferred` **when no direction is printed**" does not apply and `extracted` is correct; run2's `inferred` is the over-cautious reading. |

## Gold corrections

- **`mpn`** — gold says `ADS1015IDGS`; the datasheet never prints that string. **Verdict: RUN** (both runs are right). The PACKAGE OPTION ADDENDUM on p.39 lists only `ADS1015IDGSR` and `ADS1015IDGST` ("ADS1015IDGSR  Active  Production  VSSOP (DGS) | 10  2500  LARGE T&R", p.39), which is what both runs recorded.
  Because: reference.md defines `mpn` as the "manufacturer part number", and SKILL.md forbids filling a value the datasheet does not state — `ADS1015IDGS` is a KiCad-side package-only form, not a TI orderable. Low practical impact (the family and geometry are identical) but it is a value not on any page.

No other gold field looks wrong on a full read of p.3, p.47 and p.48: the family `VSSOP`, `pin_count` 10, `pitch` `8X 0.5`, `lead_width` `10X 0.27 / 0.17` (top view, vertical arrow across one lead), `lead_thickness` `0.23 TYP / 0.13` (side view, arrow across lead material), `height` `1.1 MAX`, the 2.9–3.1 body split (datum **A** / NOTE 3 = along the rows = `body_length`, datum **B** / NOTE 4 interlead flash = across = `body_width`) and the three `land_*` values (horizontal pads, so `10X (1.45)` = along the lead, `10X (0.3)` = across, `(4.4)` between row centrelines) all match the drawings. The deliberate omissions (`2X 2` lead centre-to-centre span, `0.1 C`, `0°-8°`, `R0.05 TYP`, mask notes) are right per the rules.

## Counts

| verdict | count |
|---|---|
| GOLD | 6 |
| RUN | 0 |
| BOTH | 2 |
| NEITHER | 0 |

Plus one unflagged gold error found on my own scan: `mpn` → RUN (see Gold corrections), making the overall tally GOLD 6 / RUN 1 / BOTH 2 / NEITHER 0.

# Adjudication: drv8871_soic8

PDF sha256 `09de551aa0c6d090fd14b000634cfd894d782a050eed13110fe2eb10f1b548bf` (matches all three specs), 27 pages.
Package outline `DDA0008B` = PDF p.24; land pattern `EXAMPLE BOARD LAYOUT` = PDF p.25; pin configuration / Pin Functions = p.3.

## Findings

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| pins[1].group (pin 1 `GND`) | `"power"` | absent | absent | RUN | 3 | p.3 prints `GND 1 PWR` in the TYPE column and reference.md names "the supply pins `power`" as a group value; three PWR pins form that block. |
| pins[5].group (pin 5 `VM`) | `"power"` | absent | absent | RUN | 3 | Same PWR block: p.3 table row reads `VM 5 PWR` / "6.5-V to 45-V power supply". |
| pins[7].group (pin 7 `PGND`) | `"power"` | absent | absent | RUN | 3 | p.3 row `PGND 7 PWR High-current ground path` — third member of the printed PWR block. |
| pins[9].group (pin 9 `PAD`) | `"power"` | absent | absent | RUN | 3 | p.3 `PAD — — Thermal pad` … "Connect to board ground", i.e. tied to board ground like pins 1/7, so it belongs to the same supply block (weakest of the four). |
| dims.lead_thickness | absent | nom 0.25 | min 0.10 / max 0.25 | GOLD | 24 | p.24 front view prints the stacked pair `0.25 TYP / 0.10` with arrows across the lead toe — a stacked pair gives min+max; run2 dropped the 0.10 limit, and its quote `0.25 C A B` is the datum feature-control frame ⌀0.25(M)\|C\|A\|B, not a dimension. |
| dims.standoff | min 0.10 / max 0.25 | min 0.00 / max 0.15 | min 0.00 / max 0.15 | GOLD | 24 | DETAIL A prints `0.15 / 0.00` from the dashed GAGE PLANE line down to the lead's bottom face; run1 used the lead-thickness values (`0.25 TYP / 0.10`) under the wrong name. |
| dims.land_ep_size | nom 2.71 | nom 2.71 | nom 2.95 | GOLD | 25 | `(2.71)`/`(3.4)` are labelled "SOLDER MASK OPENING" on the green inner rectangle; the copper pad 9 is the dashed outer rectangle `(2.95) NOTE 9` × `(4.9) NOTE 9` = "METAL COVERED BY SOLDER MASK" — and `land_ep_size` becomes a copper pad in `gen/footprint.py:145-147`. |

## Gold corrections

- **`pins[].group` on pins 1, 5, 7 (and 9)** — gold omits `group`; run1's value is `"power"`. `reference.md` lists the
  group values as "two identical amplifiers, a quad gate: `"A"`, `"B"`, and the supply pins `"power"`", and the datasheet
  prints the block itself: p.3 TYPE column gives `PWR` for `GND 1` (quote "GND 1 PWR Logic ground"), `VM 5`
  (quote "VM 5 PWR") and `PGND 7` (quote "PGND 7 PWR High-current ground path"). Pin 9 (quote "PAD — — Thermal pad",
  "Connect to board ground") is the exposed pad tied to board ground, the same supply/ground block — that one is the
  softest of the four, but nothing in the rules excludes it and the gold's own review gives no datasheet reason.
  Because: this gold is the outlier in the set — the same reference sentence is applied to `tlc555_soic8` (GND 1 and
  VDD 8 both `group: "power"`) and, per that gold's own review item 7, to `lm358_soic8` (V−/V+). For DRV8871 there is a
  three-pin supply block, which is a stronger case than either.
- **No other gold corrections.** Unflagged fields were checked against the drawings and hold: `overall_width` 5.8–6.2 is
  the tip-to-tip `6.2 TYP / 5.8` across the rows (p.24); `body_length` 4.8–5.0 and `body_width` 3.8–4.0 are read on the
  correct axes (p.24 top view); `ep_size` 2.11–2.71 is the across-the-rows pair, the 2.8–3.4 pair running along the rows
  (p.24 bottom view); `land_span` 5.4, `land_pad_length` 1.55, `land_pad_width` 0.6 (p.25); pin numbers/names/types match
  the p.3 figure and Pin Functions table, including `PAD` unnumbered → 9 `inferred`; `family: SOIC` is the name on the
  p.24 drawing that defines every dimension; `mpn: DRV8871` is the PART NUMBER printed on p.1.

Unscored, harmless: run2 marks `extracted` dimensions (`body_length`, `body_width`, `overall_width`, `lead_width`,
`lead_length`) as `inferred` (over-cautious, costs a reviewer time), and run1 marks `land_span` `extracted` where gold says
`inferred`. Neither is a value disagreement.

## Counts

| verdict | count |
|---|---|
| GOLD | 3 |
| RUN | 4 |
| BOTH | 0 |
| NEITHER | 0 |

# Adjudication: mcp23008_soic18

Datasheet: `mcp23008.pdf`, sha256 `3516fba5df6da78c2e7a58defaf90e4bdb9fb71f904e56b74b502fab0b4d112c` (43 pages;
PDF index == printed page). Package: SOIC-18 wide, drawing `C04-051D` (p.32-33), land pattern `C04-2051A` (p.34).

## Findings

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| pin 9 `group` | `power` | `power` | absent | BOTH | 4 | reference.md names the supply pins `"power"` as a group value, but gates `group` on "repeated, identical functional blocks", and VSS is a ground while VDD is a supply — the page-4 pinout shows no block structure to group. |
| pin 18 `group` | `power` | `power` | absent | BOTH | 4 | Same rule tension as pin 9: `"power"` is explicitly listed as a supply group value, yet VDD/VSS are not repeated identical blocks in the p.4 pinout. |
| `land_pad_width` | `max 0.60` | `nom 0.60` | `nom 0.60` | GOLD | 34 | P.34 prints one number per land row, `Contact Pad Width (X18) X 0.60`; reference.md says "one number in a land pattern" gets `nom`, which is the specific land-pattern rule over the generic MAX rule. |
| `land_pad_length` | `max 1.90` | `nom 1.90` | `nom 1.90` | GOLD | 34 | P.34 prints `Contact Pad Length (X18) Y 1.90` as a single value; same "one number in a land pattern → `nom`" rule. |
| `body_length` | `nom 11.55` (extracted) | absent | `nom 11.55` (inferred) | GOLD | 32 | The top view's `D` extension lines drop onto the moulded body's left/right edges, and the gull-wing leads stop inside them (only `E`, arrowed to the "2X 18 TIPS" leaders, is tip-to-tip), so `D` = `body_length`; note 3 "Dimension D does not include mold flash" confirms it is a moulded-body dimension. |
| `overall_length` | absent | `nom 11.55` | absent | GOLD | 32 | No tip-to-tip dimension exists along the pin rows on sheet 1 of 2 — `D` (11.55 BSC) is body-to-body — so there is no `overall_length` to record. |
| pin 1 `alt_names` | `[]` | `["SCK"]` | `[]` | GOLD | 2 | The p.2 MCP23008 PDIP/SOIC figure prints only `SCL` on pin 1; `SCK` is the MCP23S08 function of that pad (p.3), not a second function of this part. |
| pin 2 `alt_names` | `[]` | `["SI"]` | `[]` | GOLD | 2 | P.2 figure prints `SDA` on pin 2 only; `SDA/SI` on p.4 and `SI` on p.3 are the MCP23S08 name for the same pad. |
| pin 3 `alt_names` | `[]` | `["SO"]` | `[]` | GOLD | 2 | P.2 figure prints `A2` on pin 3; `A2/SO` (p.4) pairs `A2` with the MCP23S08 serial output, so `SO` is not an alt function of the MCP23008. |
| pin 7 `alt_names` | `[]` | `["CS"]` | `[]` | GOLD | 2 | P.2 figure prints `NC` on pin 7; `NC/CS` (p.4) is MCP23008-NC paired with MCP23S08 chip select. |
| pin 3 `status` | `extracted` | `inferred` | `extracted` | GOLD | 4 | `input` is read, not derived: the p.2 figure draws a one-way arrow into pin 3 and the p.4 function cell reads "Hardware address input (**MCP23008**)" — a printed port description, which reference.md allows for `extracted`; `input` is not one of the types the rules force to `inferred`. |
| pin 7 `status` | `extracted` | `inferred` | `extracted` | GOLD | 4 | `no_connect` is printed outright — pin name `NC/CS`, function "No connect (**MCP23008**)", and a bare line with no arrow in the p.2 figure; reference.md's type table does not mark "not connected" as an inferred type (unlike supply/open-drain rows). |

Note: run1 vs gold also differed on `standoff`-adjacent cosmetics only — run1's `body_length` is `extracted` where gold says `inferred`; that field is not scored, and both agree the number had to be interpreted, so no row above.

## Gold corrections

- **`pins[6].name` = `RESET` (should be `RESET-`)** — no run records the polarity either, so the scorer saw no disagreement.
  Gold says `RESET` (quote "RESET 6 4 6 I External Reset input. Must be biased externally.", p.4); the p.4 table prints
  RESET with an **overbar** and the p.2 figure draws `RESET̅` on pin 6, i.e. active low. reference.md: "`name`: the
  primary function as printed. Use the ASCII hyphen (`IN1-`, `V-`)" — the two examples it gives are exactly overbar
  names, so the ASCII form is `RESET-`. Because: the JSON name field does have an ASCII carrier for the overbar
  (the trailing hyphen), so dropping it loses the active-low polarity for no reason; KiCad's own
  `MCP23008-xSO` stores `~{RESET}` (Interface_Expansion.kicad_sym).
- Considered and **not** an error: pin 8 `INT` as plain `output` even though p.4 says it "Can be configured for
  active-high, active-low or open-drain" — the open drain is a configuration option, not the pin's printed
  direction, and the rules reserve the special types for what the pin's row actually says.

## Counts

| verdict | count |
|---|---|
| GOLD | 10 |
| RUN | 0 |
| BOTH | 2 |
| NEITHER | 0 |

# Adjudication: sn74lvc2t45_vssop8

Datasheet sha256 `f0dc4a7a46a5b2020117e8bec614aec33f4f15784a82ab73dc3fa5f91d5c86bc` matches the gold's
`datasheet.sha256`. All dimension evidence is on **page 31** (`DCU0008A` package outline); land-pattern
evidence is on page 32. The top view on p.31 has the two pin rows running **vertically** (1–4 down the
left edge, 8–5 down the right edge), so "across the rows" is the horizontal direction of the top view —
this fixes the three outline dimensions, checked on the 300 dpi render.

## Findings

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| dims.height | max 0.9 (quote "VSSOP - 0.9 mm max height") | min 0.6 / max 0.9 | min 0.6 / max 0.9 | GOLD | 31 | Detail A prints the stack `0.9` over `0.6` between the package top and the seating plane — a printed range, which reference.md says takes min **and** max; run1 kept only the title-block max and dropped the 0.6 (run2 has the right pair). |
| dims.lead_thickness | min 0.2 / max 0.35 | absent | nom 0.13 | GOLD | 31 | Front view dimensions the lead toe vertically as `(0.13) TYP`; run1 put the Detail A horizontal foot callout `0.35/0.20` here — that is the foot length, not thickness. |
| dims.lead_length | absent | absent | min 0.2 / max 0.35 | GOLD | 31 | Detail A prints `0.35` over `0.20` as a horizontal dimension running from the lead heel to the end of the flat foot — the foot length; both runs omitted it. |
| dims.lead_width | min 0.17 / max 0.25 | absent | min 0.17 / max 0.25 | GOLD | 31 | Top view prints `8X 0.25` over `0.17` with arrows straddling one lead (run1's value, confirmed); run2 omitted it. |
| dims.overall_width | min 3.0 / max 3.2 | min 2.2 / max 2.4 | min 3.0 / max 3.2 | GOLD | 31 | The `3.2 / 3.0 TYP` callout's extension lines drop to the **lead tips** on both edges (left lead tip and right lead tip), i.e. tip-to-tip across the rows = `overall_width`; run2 filed it as `body_length`. |
| dims.body_width | min 2.2 / max 2.4 | min 1.9 / max 2.1 | min 2.2 / max 2.4 | GOLD | 31 | The bottom `2.4 / 2.2 NOTE 3` callout's extension lines land on the two **body** edges across the rows; run2 swapped it with the vertical callout. |
| dims.body_length | min 1.9 / max 2.1 | min 3.0 / max 3.2 | min 1.9 / max 2.1 | GOLD | 31 | The left-hand `2.1 / 1.9 NOTE 3` callout runs vertically between the body top and bottom edges, i.e. along the pin rows = `body_length`; run2 filed it as `body_width`. |
| dims.standoff | min 0.0 / max 0.1 | nom 0.12 | min 0.0 / max 0.1 | GOLD | 31 | Detail A's `0.1/0.0` arrows run from the seating plane up to the lead's underside; the boxed basic `0.12 GAGE PLANE` is a separate dimension to the dotted coplanarity plane, which the drawing deliberately places above the lead underside, so it is not the standoff (run1 has the right pair). |

Notes on method: run2's three-way swap of `3.2/3.0`, `2.4/2.2` and `2.1/1.9` is one misreading repeated
three times — the values themselves are all printed on p.31, only the names are wrong; the extension-line
landing points (lead tip vs body edge, horizontal vs vertical) decide all three. Run1's `lead_thickness`
and missing `lead_length` are the same misread: the Detail A horizontal callout `0.35/0.20` was recorded
under the wrong name, so the foot length was lost.

## Gold corrections

- None. No item came out RUN or NEITHER, and my own scan of the full gold spec against the datasheet
  found no wrong field.

Suspects checked on my own scan (both runs agreed with gold, so they were worth testing):

- **`mpn`** — both runs say `SN74LVC2T45DCU`, gold says `SN74LVC2T45DCUR`. Gold is right: the bare
  `SN74LVC2T45DCU` is not an orderable part number. The addendum on p.22 lists `SN74LVC2T45DCUR`
  ("VSSOP (DCU) | 8 | 3000 | LARGE T&R") alongside `SN74LVC2T45DCUT`/`SN74LVC2T45DCUTG4`; page 1 only
  names the package ("DCU (VSSOP, 8)"). Verdict GOLD.
- **land pattern (`land_pad_length` 0.85, `land_pad_width` 0.3, `land_span` 3.1, p.32)** — checked on
  the render: `8X (0.85)` is the pad's horizontal extent (along the lead direction), `8X (0.3)` its
  vertical extent, and `(3.1)` spans between the two pad-row centrelines. Gold correct.
- **Pins (p.2)** — Figure 4-1 confirms 1 VCCA, 2 A1, 3 A2, 4 GND, 5 DIR, 6 B2, 7 B1, 8 VCCB, matching
  Table 4-1; types and `inferred` statuses are right per reference.md.
- **Omitted dimensions** — `body_thickness` (p.31 gives no separate body height), `overall_length` (no
  tip-to-tip dimension along the rows), and the lead centre-to-centre span `2X 1.5` (reference.md: a lead
  centre-to-centre span is not recorded) are correctly left out. `exposed_pad: false`, `pin_count: 8`,
  `family: VSSOP` are correct.

## Counts

| verdict | count |
|---|---|
| GOLD | 8 |
| RUN | 0 |
| BOTH | 0 |
| NEITHER | 0 |

# Adjudication: tlc555_soic8

All outline verdicts rest on the render of PDF page 38 (`D0008A`, PACKAGE OUTLINE, 4214825/C 02/2019),
specifically DETAIL A (bottom right) and the side view; land values on PDF page 39; pin values on PDF page 3.

## Findings

| item | run1 | run2 | gold | verdict | page | reason |
|---|---|---|---|---|---|---|
| dims.lead_length | absent | nom 1.04, quote "(.041)" | min 0.41 / max 1.27, quote "[0.41-1.27]" | GOLD | 38 | In DETAIL A the `.016-.050 [0.41-1.27]` arrow runs lead tip → tangent of the foot bend (foot length), while `(.041) [1.04]` runs lead tip → body face — the body-to-tip length `reference.md` explicitly excludes ("Nexperia `L`, ST `L1` … leave it out"); run1 dropped it, run2 took the excluded callout. |
| dims.standoff | min 0.11 / max 0.25, quote "[0.11-0.25]" | min 0.13 / max 0.25, quote ".005-.010 TYP" | absent | RUN | 38 | DETAIL A prints `.004-.010 [0.11-0.25]` with the arrow spanning the body underside to the seating plane — exactly `reference.md`'s "gap between the seating plane and the body underside"; run1's value is the correct one (run2 mistakenly reused the lead-thickness callout). |
| dims.lead_thickness | min 0.13 / max 0.25, quote ".005-.010 TYP [0.13-0.25]" | nom 0.25, quote ".010 [0.25]" | absent | RUN | 38 | The side view prints `.005-.010 TYP [0.13-0.25]` with arrows straddling the flattened foot (JEDEC MS-012 `c` = lead thickness); run1's value is correct, run2's `nom 0.25` is the ⌖ C A B coplanarity/seating-plane tolerance, not a size. |
| pin 1 `group` | `"power"` | absent | `"power"` | BOTH | 3 | `reference.md` lists "the supply pins `power`" among the allowed group values but conditions `group` on "repeated, identical functional blocks"; a single-timer TLC555 shows no such block, so omitting it is equally permitted (the gold's own review says "Either is defensible"). |
| pin 8 `group` | `"power"` | absent | `"power"` | BOTH | 3 | Same call as pin 1 — rules permit both, datasheet shows no repeated block. |

## Gold corrections

- **`package.dimensions.standoff`** — gold omits it; the datasheet prints `.004-.010 [0.11-0.25]` on p. 38 with the arrow spanning body underside to the seating plane, which `reference.md` defines verbatim as `standoff`. Correct value: `min 0.11, max 0.25`, quote `".004-.010 [0.11-0.25]"`, p. 38.
  Because: the gold's omission rests on `evals/README.md` "Conventions" ("the SOIC `.004-.010` and `.005-.010` values" are called out as ambiguous) — an eval-harness convention the runs never saw. Against the rules the runs actually had (`reference.md`), the callout is not ambiguous: the page prints "SEATING PLANE" itself.
- **`package.dimensions.lead_thickness`** — gold omits it; the datasheet prints `.005-.010 TYP [0.13-0.25]` on p. 38, arrows straddling the flattened foot in the side view. Correct value: `min 0.13, max 0.25` (`TYP` on a range still gives min/max per `reference.md`), quote `".005-.010 TYP [0.13-0.25]"`, p. 38. Same reason as above.
- **`package.dimensions.overall_width` / `body_length` / `body_width` — `status`** — gold marks all three `extracted` but `land_span` `inferred`. Assigning `.228-.244` to `overall_width`, `.189-.197` to `body_length` and `.150-.157` to `body_width` required reading which axis each arrow runs along (gold review §2.5), which is the exact case `reference.md` says to mark `inferred` ("which side of the drawing it measures"). Run 1 independently reached this for `overall_width` (`inferred`), which is the safer label and the one the rules ask for.

Checked and found **correct** in the gold (no change): `lead_length` 0.41–1.27, `land_span` 5.4 (the p. 39 `(.213) [5.4]` arrow runs pad-1 centreline to pad-5 centreline — row centre-to-centre, not within-row), `land_pad_length` 1.55, `land_pad_width` 0.6, all eight pin numbers/names/types, and the absence of any `no_connect` entry (Table 4-1's `NC` row prints an em dash in the PIN NO. column — p. 3).

## Counts

| verdict | count |
|---|---|
| GOLD | 1 |
| RUN | 2 |
| BOTH | 2 |
| NEITHER | 0 |


---

# Merged counts

Scored items (the disagreements the scorer printed, one row per item):

| verdict | ads1015_vssop10 | drv8871_soic8 | mcp23008_soic18 | sn74lvc2t45_vssop8 | tlc555_soic8 | total |
|---|---|---|---|---|---|---|
| GOLD | 6 | 3 | 10 | 8 | 1 | **28** |
| RUN | 0 | 4 | 0 | 0 | 2 | **6** |
| BOTH | 2 | 0 | 2 | 0 | 2 | **6** |
| NEITHER | 0 | 0 | 0 | 0 | 0 | **0** |
| items | 8 | 7 | 12 | 8 | 5 | **40** |

Additional gold errors the scorer could not see (both runs agreed with the gold, or the field is not
scored at all), all judged **RUN** (gold wrong):

| case | field | verdict | source |
|---|---|---|---|
| ads1015_vssop10 | `mpn` | RUN | child adjudicator's own full-gold scan |
| mcp23008_soic18 | `pins[6].name` | RUN | child adjudicator's own full-gold scan |
| tlc555_soic8 | 3 dimension `status` labels | RUN | child adjudicator's own full-gold scan |

**Grand tally: GOLD 28 · RUN 9 · BOTH 6 · NEITHER 0 (40 scored items + 3 unflagged).**

Read the 6 RUN verdicts and the 3 unflagged gold errors together: they are not random. Two of them are
the same rule gap and one is a convention the runs never saw (see the merged Gold corrections).

---

# Merged gold corrections

Every change below is to a gold file under `gold/<case>/spec.gold.json`. **None has been applied.**

## ads1015_vssop10

- **`mpn`** — gold says `ADS1015IDGS`; the datasheet never prints that string. Verdict RUN (both runs
  agree, so the scorer saw nothing). The PACKAGE OPTION ADDENDUM on p.39 lists only `ADS1015IDGSR` and
  `ADS1015IDGST` ("ADS1015IDGSR  Active  Production  VSSOP (DGS) | 10  2500  LARGE T&R", p.39), which
  is what both runs recorded. `reference.md` defines `mpn` as the manufacturer part number and SKILL.md
  forbids filling a value the datasheet does not state; `ADS1015IDGS` is a KiCad-side package-only form,
  not a TI orderable. Low practical impact (identical family and geometry).

## drv8871_soic8

- **`pins[].group` on pins 1, 5, 7 and 9** — gold omits `group`; run1's value is `"power"`. Verdict RUN.
  `reference.md` lists the group values as "two identical amplifiers, a quad gate: `"A"`, `"B"`, and
  the supply pins `"power"`", and the datasheet prints the block itself: p.3 TYPE column gives `PWR` for
  `GND 1` ("GND 1 PWR Logic ground"), `VM 5` ("VM 5 PWR") and `PGND 7` ("PGND 7 PWR High-current
  ground path"). Pin 9 ("PAD — — Thermal pad", "Connect to board ground") is the exposed pad tied to
  board ground — the softest of the four, but nothing in the rules excludes it and the gold's own review
  gives no datasheet reason. This gold is the outlier in the set: the same reference sentence is applied
  to `tlc555_soic8` (GND 1 / VDD 8) and, per that gold's review item 7, to `lm358_soic8` (V−/V+); here
  there is a three-pin supply block, a stronger case than either.

## tlc555_soic8

- **`package.dimensions.standoff`** — gold omits it. Verdict RUN (run1 is right). Correct value:
  `min 0.11, max 0.25`, quote `".004-.010 [0.11-0.25]"`, p.38. The arrow spans body underside to the
  seating plane, which `reference.md` defines verbatim as `standoff`.
- **`package.dimensions.lead_thickness`** — gold omits it. Verdict RUN (run1 is right). Correct value:
  `min 0.13, max 0.25`, quote `".005-.010 TYP [0.13-0.25]"`, p.38 (arrows straddling the flattened foot
  in the side view). `TYP` on a range still gives min/max per `reference.md`.
- **`package.dimensions.overall_width` / `body_length` / `body_width` — `status`** — gold marks all three
  `extracted` but marks `land_span` `inferred`. Verdict RUN. Assigning `.228-.244` to `overall_width`,
  `.189-.197` to `body_length` and `.150-.157` to `body_width` required reading which axis each arrow
  runs along (gold review §2.5) — exactly the case `reference.md` says to mark `inferred` ("which side
  of the drawing it measures"). The gold is internally inconsistent here. Run 1 independently reached
  `inferred` for `overall_width`.
  Because all three rest on the gold's own `evals/README.md` "Conventions" note that "the SOIC `.004-.010`
  and `.005-.010` values" are ambiguous callouts: a convention of the eval harness that the runs were
  never shown. Against the rules the runs actually had, the page prints "SEATING PLANE" itself.

## mcp23008_soic18

- **`pins[6].name` = `RESET`, should be `RESET-`** — no run records the polarity, so the scorer saw no
  disagreement. Verdict RUN. Gold says `RESET` (quote "RESET 6 4 6 I External Reset input. Must be
  biased externally.", p.4); the p.4 table prints RESET with an **overbar** and the p.2 figure draws
  `RESET̅` on pin 6, i.e. active low. `reference.md`: "`name`: the primary function as printed. Use the
  ASCII hyphen (`IN1-`, `V-`)" — its two examples are exactly overbar names, so the ASCII form is
  `RESET-`. KiCad's own `MCP23008-xSO` symbol stores `~{RESET}`.

## sn74lvc2t45_vssop8

- **None.** No item came out RUN or NEITHER, and a full-gold scan against the datasheet found no wrong
  field (mpn, land pattern, pin table/figure pairings and the deliberately omitted dimensions were all
  checked and are right).
