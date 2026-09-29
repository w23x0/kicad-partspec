# PartSpec reference

```
{
  "mpn": "…",                       manufacturer part number as it should appear in KiCad
  "manufacturer": "…",
  "datasheet": {"sha256": "…", "revision": "…", "url": "…" (optional)},
  "package": {
    "family": "SOIC | TSSOP | QFN | VQFN | QFP | TQFP | …",
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
- `group`: only when the part has separate units, e.g. two identical amplifiers: `"A"`, `"B"`, and the supply pins `"power"`.
  Omit it otherwise.
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
| `overall_length`, `overall_width` | lead tip to lead tip, for leaded packages (dual-row: across the rows is `overall_width`) |
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

Values in parentheses on a drawing are reference values; they are fine to use for `land_*`. If you have to interpret what a
number is (for example which side of the drawing it measures), mark that dimension `inferred`.
