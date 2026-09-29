"""Generate a KiCad symbol library (``.kicad_sym``) from a PartSpec.

Layout is deterministic and grid-aligned.  Pins are placed on the 1.27 mm grid;
units follow ``Pin.group`` (a group named ``power`` becomes the last unit, the
way KiCad's own libraries lay out multi-unit parts).  The output targets KiCad
9's file format (version 20241209).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

from partspec.sexpr import Atom, write_sexpr
from partspec.spec.model import PartSpec, Pin

FORMAT_VERSION = "20241209"
GRID = 1.27
PIN_PITCH = 2.54
PIN_LENGTH = 2.54
FONT = 1.27
# Rough width of one glyph at the font size above, used only to size the body.
CHAR_WIDTH = 1.2
MIN_HALF_WIDTH = 5.08
# Distance from a pin's inner end to the start of its name (the symbol's pin_names offset).
NAME_OFFSET = 1.016

_GROUND = re.compile(r"(?i)^(?:VSS\w*|V-|VEE|EP|PAD)$|GND")
_RIGHT_TYPES = {"output", "open_collector", "open_emitter", "tri_state"}
_POWER_TYPES = {"power_in", "power_out"}

# side -> angle of a pin on that side (direction pointing into the body)
_ANGLE = {"left": 0, "right": 180, "top": 270, "bottom": 90}


def _natural_key(value: str) -> list[Any]:
    return [(0, int(part)) if part.isdigit() else (1, part) for part in re.split(r"(\d+)", value) if part]


def _ceil_to(value: float, step: float) -> float:
    return math.ceil(value / step - 1e-9) * step


def _effects(*, hide: bool = False) -> list[Any]:
    node: list[Any] = [Atom("effects"), [Atom("font"), [Atom("size"), FONT, FONT]]]
    if hide:
        node.append([Atom("hide"), Atom("yes")])
    return node


def _property(name: str, value: str, x: float, y: float, *, hide: bool = False) -> list[Any]:
    return [Atom("property"), name, value, [Atom("at"), x, y, 0], _effects(hide=hide)]


def unit_groups(pins: tuple[Pin, ...]) -> list[str | None]:
    """Ordered unit keys: named groups in first-seen order, ``power`` last, ungrouped after."""
    named: list[str] = []
    for pin in pins:
        if pin.group is not None and pin.group not in named:
            named.append(pin.group)
    named.sort(key=lambda group: group.lower() == "power")  # stable: only moves "power" to the end
    keys: list[str | None] = list(named)
    if any(pin.group is None for pin in pins):
        keys.append(None)
    return keys


def _assign_sides(pins: list[Pin]) -> dict[str, list[Pin]]:
    sides: dict[str, list[Pin]] = {"left": [], "right": [], "top": [], "bottom": []}
    rest: list[Pin] = []
    for pin in pins:
        if pin.electrical_type == "power_in" and _GROUND.search(pin.name):
            sides["bottom"].append(pin)
        elif pin.electrical_type in _POWER_TYPES:
            sides["top"].append(pin)
        elif pin.electrical_type == "input":
            sides["left"].append(pin)
        elif pin.electrical_type in _RIGHT_TYPES:
            sides["right"].append(pin)
        else:
            rest.append(pin)
    for pin in sorted(rest, key=lambda item: _natural_key(item.number)):
        target = "left" if len(sides["left"]) <= len(sides["right"]) else "right"
        sides[target].append(pin)
    for members in sides.values():
        members.sort(key=lambda item: _natural_key(item.number))
    return sides


@dataclass(frozen=True)
class _Placed:
    pin: Pin
    x: float
    y: float
    angle: int


@dataclass(frozen=True)
class _Layout:
    half_width: float
    half_height: float
    placed: list[_Placed]
    has_top: bool
    has_bottom: bool


def _layout(pins: list[Pin]) -> _Layout:
    """Place the pins of one unit around a rectangle sized to keep every name readable."""
    sides = _assign_sides(pins)
    rows = max(len(sides["left"]), len(sides["right"]), 1)
    cols = max(len(sides["top"]), len(sides["bottom"]), 1)

    def chars(side: str) -> int:
        return max((len(pin.name) for pin in sides[side]), default=0)

    def vertical_extent(side: str) -> float:
        return chars(side) * CHAR_WIDTH + NAME_OFFSET + GRID / 2 if sides[side] else 0.0

    half_width = max(
        MIN_HALF_WIDTH,
        _ceil_to(((chars("left") + chars("right")) * CHAR_WIDTH + PIN_PITCH) / 2, GRID),
        _ceil_to(cols * PIN_PITCH / 2 + GRID, GRID),
    )
    # Vertical names hang inward from the top/bottom edge; the side rows must clear them.
    half_height = _ceil_to(rows * GRID + max(vertical_extent("top"), vertical_extent("bottom"), GRID), GRID)
    placed: list[_Placed] = []
    for side in ("left", "right"):
        x = -(half_width + PIN_LENGTH) if side == "left" else half_width + PIN_LENGTH
        for index, pin in enumerate(sides[side]):
            placed.append(_Placed(pin, x, ((rows - 1) / 2 - index) * PIN_PITCH, _ANGLE[side]))
    for side in ("top", "bottom"):
        y = half_height + PIN_LENGTH if side == "top" else -(half_height + PIN_LENGTH)
        for index, pin in enumerate(sides[side]):
            placed.append(_Placed(pin, (index - (cols - 1) / 2) * PIN_PITCH, y, _ANGLE[side]))
    return _Layout(half_width, half_height, placed, bool(sides["top"]), bool(sides["bottom"]))


def _pin_node(item: _Placed) -> list[Any]:
    pin = item.pin
    node: list[Any] = [
        Atom("pin"),
        Atom(pin.electrical_type),
        Atom("line"),
        [Atom("at"), item.x, item.y, item.angle],
        [Atom("length"), PIN_LENGTH],
        [Atom("name"), pin.name, _effects()],
        [Atom("number"), pin.number, _effects()],
    ]
    for alt in pin.alt_names:
        node.append([Atom("alternate"), alt, Atom(pin.electrical_type), Atom("line")])
    return node


def build_symbol(spec: PartSpec, footprint: str | None = None) -> list[Any]:
    """Build the ``(symbol ...)`` tree for one part."""
    name = spec.mpn
    layouts = [_layout([pin for pin in spec.pins if pin.group == key]) for key in unit_groups(spec.pins)]
    units: list[list[Any]] = []
    for number, layout in enumerate(layouts, start=1):
        body: list[Any] = [
            Atom("rectangle"),
            [Atom("start"), -layout.half_width, layout.half_height],
            [Atom("end"), layout.half_width, -layout.half_height],
            [Atom("stroke"), [Atom("width"), 0.254], [Atom("type"), Atom("default")]],
            [Atom("fill"), [Atom("type"), Atom("background")]],
        ]
        units.append([Atom("symbol"), f"{name}_{number}_1", body, *[_pin_node(item) for item in layout.placed]])
    # Reference and Value are shared by all units, so clear the tallest one.  Pins stick
    # out PIN_LENGTH beyond the body and their numbers sit just outside that.
    stick_out = PIN_LENGTH + GRID
    above = GRID + max(item.half_height + (stick_out if item.has_top else 0) for item in layouts)
    below = GRID + max(item.half_height + (stick_out if item.has_bottom else 0) for item in layouts)
    description = f"{spec.manufacturer} {spec.mpn}, {spec.package.family}-{spec.package.pin_count}"
    return [
        Atom("symbol"),
        name,
        [Atom("pin_names"), [Atom("offset"), NAME_OFFSET]],
        [Atom("exclude_from_sim"), Atom("no")],
        [Atom("in_bom"), Atom("yes")],
        [Atom("on_board"), Atom("yes")],
        _property("Reference", "U", 0, above),
        _property("Value", spec.mpn, 0, -below),
        _property("Footprint", footprint or "", 0, 0, hide=True),
        _property("Datasheet", spec.datasheet.url or "", 0, 0, hide=True),
        _property("Description", description, 0, 0, hide=True),
        *units,
        [Atom("embedded_fonts"), Atom("no")],
    ]


def build_library(spec: PartSpec, footprint: str | None = None) -> list[Any]:
    return [
        Atom("kicad_symbol_lib"),
        [Atom("version"), Atom(FORMAT_VERSION)],
        [Atom("generator"), "partspec"],
        [Atom("generator_version"), "0.0.1"],
        build_symbol(spec, footprint),
    ]


def render_library(spec: PartSpec, footprint: str | None = None) -> str:
    return write_sexpr(build_library(spec, footprint))
