# PartSpec reference

```
{
  "mpn": "…",                       manufacturer part number as the datasheet prints it
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

`mpn` is that string copied exactly: the orderable the datasheet's addendum lists, suffix and all (`ADS1015IDGSR`), not a
package-only form that appears on no page (`ADS1015IDGS`). Drop a tape-and-reel or temperature suffix only when the page
prints the shorter number. If the datasheet prints no orderable, use the number it does print and say so in the hand-over.

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
- An `alt_names` entry is another function of the same pad **on the part you were asked for**. When one datasheet documents
  several parts, a cell that pairs your pin with a sibling part's name (`SCL/SCK`, `A2/SO`, `NC/CS` on the MCP23008 pages) is
  two parts, not two functions: take the name printed for your part, leave `alt_names` empty, and list the pairing in the
  hand-over. The same goes for a name from another package's pinout column or table.
- `group`: only when the datasheet shows repeated, identical functional blocks — two identical amplifiers, a quad gate:
  `"A"`, `"B"`, `"C"`. The two sides of one function are not units, so the A port and B port of a level translator, the two
  banks of a memory, or an input port and its matching output port stay ungrouped.
- The supply pins are the one exception to "identical": `"power"` marks them as supplies, not as repeated blocks, so the
  rule above does not gate it. When the datasheet prints the supplies as a block of their own — a `PWR` cell in a TYPE
  column (DRV8871's `GND 1 PWR`, `VM 5 PWR`, `PGND 7 PWR`) — group that block `"power"`, whether or not anything else on
  the part is grouped. A lone supply or ground pin, or a bare printed VDD/VSS pair on a part that prints no supply block of
  its own, is neither a unit nor a printed block: grouping it `"power"` is optional, and leaving `group` off it is equally
  correct. Omit `group` on a pin that is neither a unit nor a supply.
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

Read the rendered page before you name a callout — the numbers are all on the text layer, the names are not. Follow each
callout's extension lines and see which way its arrow runs:

- extension lines landing on the **lead tips** of both rows: tip-to-tip across the rows, so `overall_width`;
- extension lines landing on the **moulded body** edges: the body, `body_length` along the pin rows or `body_width` across;
- an arrow from the tip of one row to the tip of the other **along** the rows: `overall_length`. If the drawing prints no
  such callout, leave `overall_length` out rather than naming a body dimension for it.

A boxed basic dimension, or one labelled `GAGE PLANE`, is a reference plane or a datum, not a size: never record it as
`standoff`, `lead_length`, `lead_thickness` or anything else. The three lead dimensions come from DETAIL A's arrows —
`standoff` from the body underside down to the seating plane, `lead_length` along the flat foot from the lead tip to where
the bend starts, `lead_thickness` from the arrows straddling the lead material itself, where a `TYP` supplies `nom`.

`land_pad_length`, `land_pad_width`, `land_span` and `land_ep_size` are metal, so take them from the rectangle that is the
metal: the pad outline, the plain pad callouts, or the rectangle a note calls "METAL COVERED BY SOLDER MASK". A second
rectangle labelled "SOLDER MASK OPENING" is the mask, not the pad (DRV8871 records `(2.95)`, not the `(2.71)`), and it is
not recorded. When the drawing prints only the mask opening, say so in the hand-over instead of substituting it.

Values in parentheses on a drawing are reference values; they are fine to use for `land_*`. If you have to interpret what a
number is (for example which side of the drawing it measures), mark that dimension `inferred`.

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

The lead length from the body face to the tip (Nexperia `L`, ST `L1`, and any such callout on any vendor's drawing) is
not our `lead_length`; leave it out. The foot, from the tip to where the bend starts, is.
