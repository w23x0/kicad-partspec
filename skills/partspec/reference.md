# PartSpec reference

```
{
  "mpn": "…",                       manufacturer part number as it should appear in KiCad
  "manufacturer": "…",
  "datasheet": {"sha256": "…", "revision": "…", "url": "…" (optional)},
  "package": {
    "family": "SOIC | TSSOP | SOT-23 | QFN | VQFN | QFP | TQFP | …",
    "pin_count": 8,                 leads/pads, not counting an exposed pad
    "exposed_pad": false,
    "dimensions": { "<name>": {"min": …, "nom": …, "max": …, "source": {"page": 1, "quote": "…"}, "status": "extracted"} }
  },
  "pins": [ {"number": "1", "name": "…", "electrical_type": "…", "alt_names": ["…"], "group": "…",
             "source": {"page": 1, "quote": "…"}, "status": "extracted"} ]
}
```

Give whichever of `min`/`nom`/`max` the datasheet prints:

- a range (`4.81-5.00`), or two numbers stacked on the drawing (`1.0` over `0.8`), gets `min` and `max`;
- a typical value (`TYP`, `BSC`, one number in a land pattern) gets `nom`;
- a value marked `MAX` gets only `max`;
- `X ± t` gets all three: `min` = X - t, `nom` = X, `max` = X + t (the text layer often drops the `±`, so check the image);
- a row printed once for two symbols (`D/E`, `D1/E1`) gives both dimensions the same values.

Pin `number` is a string (`"1"`, `"A1"`).

## Pin fields

- `name`: the primary function as printed. Use the ASCII hyphen (`IN1-`, `V-`). Extra *functions* of a multi-function pin go
  in `alt_names` (`PB0 (PCINT0/CLKO/ICP1)` is name `PB0`, alt_names `PCINT0`, `CLKO`, `ICP1`). A description is not an
  alternate function: an exposed pad is named `EP` and gets no `alt_names`.
- `group`: only when the datasheet shows repeated, identical functional blocks — two identical amplifiers, a quad gate:
  `"A"`, `"B"`, and the supply pins `"power"`. The two sides of one function are not units, so the A port and B port of a
  level translator, the two banks of a memory, or an input port and its matching output port stay ungrouped. Omit it
  otherwise.
- `electrical_type` is one of KiCad's:

| Datasheet says | Use |
|---|---|
| input (I) | `input` |
| output (O) | `output` |
| I/O, port pin, bidirectional | `bidirectional` |
| open drain / open collector output | `open_collector` (status `inferred`) |
| a supply pin or a ground pin, **even when the I/O column says I** | `power_in` (status `inferred`) |
| a supply the part produces | `power_out` (status `inferred`) |
| an analog-to-digital converter input channel | `input` (status `inferred` when no direction is printed) |
| an analog reference, or a pin with no signal direction at all | `passive` (status `inferred`) |
| exposed pad tied to ground | `power_in` (status `inferred`) |
| not connected | `no_connect` |
| three-state output | `tri_state` |

  Other KiCad types exist (`open_emitter`, `free`, `unspecified`); use them only if the datasheet says so.

The pin table's direction column is not the last word. Check the function table and the feature list for a high-impedance
state: a pin the part can put in Z is `tri_state` even when its row says "output" (74HC595: Q0–Q7 are high-impedance while
OE is HIGH), and a pin that can never do that stays `output` on the same part (Q7S, which OE does not gate).

## Status

`extracted`: the pin's number and name were read from the datasheet (a pairing you verified on the rendered image counts),
and its type was read from an I/O column or a port description ("bi-directional I/O port"). `inferred`: anything derived,
including every type chosen through the supply, ground, open-drain, reference or no-direction rows above, an exposed-pad
number the datasheet does not print, and any dimension whose meaning you had to interpret. Marking too much `inferred`
costs a human a little review time; marking a guess `extracted` costs a wrong part, so when unsure choose `inferred`.
`confirmed`: reserved for humans.

## Dimension names

Take each of these that the datasheet gives; skip the ones it does not.

| Name | Meaning |
|---|---|
| `pitch` | distance between neighbouring leads |
| `body_length`, `body_width` | plastic body size. Dual-row: length is along the pin rows, width is across between the rows. Quad: the two sides |
| `overall_length`, `overall_width` | lead tip to lead tip, for leaded packages (dual-row: across the rows is `overall_width`, the largest across-rows dimension on the outline; a lead centre-to-centre span is not recorded) |
| `height` | overall height above the board (usually a max) |
| `body_thickness` | body height without leads, when given separately |
| `standoff` | gap between the seating plane and the body underside |
| `lead_width` | width of one lead |
| `lead_length` | foot length of a lead |
| `lead_thickness` | thickness of a lead |
| `ep_size` | exposed pad side length from the package outline (square pads) |
| `land_pad_length` | one pad's size along the lead direction, from the example land pattern |
| `land_pad_width` | one pad's size across, from the example land pattern |
| `land_span` | centre-to-centre distance between opposite pad rows in the land pattern |
| `land_ep_size` | exposed pad size in the land pattern |

Three lead callouts are near-identical on the page and are the easiest to misread. Name each one by the two features its
extension lines run between, not by its size, its place on the sheet or the label the drawing gives it:

| The dimension spans | Name |
|---|---|
| the body underside and the seating (gage) plane | `standoff` |
| the two edges of one lead's cross-section, in the front or side view | `lead_thickness` |
| the lead tip and where the lead leaves the body — the start of the bend, the foot that rests on the board | `lead_length` |

This holds for any vendor's outline sheet, named or lettered, and inside the DETAIL A style detail view as much as on the
outline: the foot row is the same span the letter table below gives as Nexperia `Lp` / ST `L`.

When two readings of the same callout disagree about which of these three it is, the drawing is being misread, not the name:
re-render the page and say which two planes the dimension spans before naming it.

Values in parentheses on a drawing are reference dimensions — the drawing's own notes say so. They may be used for a `land_*`
value and must not become a package dimension: a parenthesised `(0.15) TYP` across a lead in a package outline is not a
`lead_thickness`, and if that is the only thickness callout on the sheet, leave `lead_thickness` out rather than record it. A
boxed `BASIC` value, such as a boxed gage-plane offset, is likewise not a package dimension: it is a basic dimension for the
land pattern. If you have to interpret what a number is (for example which side of the drawing it measures), mark that
dimension `inferred`.

Nexperia, NXP and ST print outline tables in letters where TI drawings print the names. The same letter can mean
different things per vendor, so read each one off the drawing:

| Letter | Name |
|---|---|
| `A` | `height` |
| `A1` | `standoff` |
| `A2` | `body_thickness` |
| `b`, `bp` | `lead_width` |
| `c` | `lead_thickness` |
| `D` | `body_length` |
| `e` | `pitch` |
| the body `E` (Nexperia `E`, ST `E1`) | `body_width` |
| the tip-to-tip `E` (Nexperia `HE`, ST `E`) | `overall_width` |
| the foot: the flat part resting on the board (Nexperia `Lp`, ST `L`) | `lead_length` |

The lead length from body to tip (Nexperia `L`, ST `L1`) is not our `lead_length`; leave it out.
