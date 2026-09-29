"""Artifact-layer checks: does a ``.kicad_sym`` text agree with the PartSpec?

The text is parsed again from scratch, so this verifies what was written, not
what the generator intended.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from kicad_partspec.findings import FAIL, Finding
from kicad_partspec.sexpr import as_float, children, first_child, parse_sexpr
from kicad_partspec.spec.model import PartSpec

GRID = 1.27
_EPS = 1e-6
# Text metrics used to estimate where a pin name is drawn.  They are estimates of
# KiCad's default 1.27 mm font, deliberately independent of the generator's constants.
_GLYPH_WIDTH = 1.0
_TEXT_HEIGHT = 1.27
_DEFAULT_NAME_OFFSET = 0.508


@dataclass(frozen=True)
class _SymbolPin:
    unit: int
    number: str
    name: str
    type: str
    x: float | None
    y: float | None
    angle: float | None
    length: float | None
    alternates: tuple[str, ...]


def _name_offset(symbol: list[Any]) -> float:
    names = first_child(symbol, "pin_names")
    offset_node = first_child(names, "offset") if names else None
    offset = as_float(offset_node[1]) if offset_node and len(offset_node) > 1 else None
    return _DEFAULT_NAME_OFFSET if offset is None else offset


def _name_box(pin: _SymbolPin, offset: float) -> tuple[float, float, float, float] | None:
    """Estimated (x0, y0, x1, y1) area covered by the pin name, or None when it cannot be placed."""
    if pin.x is None or pin.y is None or pin.angle is None or pin.length is None:
        return None
    span = len(pin.name) * _GLYPH_WIDTH
    half = _TEXT_HEIGHT / 2
    angle = round(pin.angle) % 360
    if angle == 0:  # pin on the left edge, name runs right
        start = pin.x + pin.length + offset
        return (start, pin.y - half, start + span, pin.y + half)
    if angle == 180:  # pin on the right edge, name runs left
        start = pin.x - pin.length - offset
        return (start - span, pin.y - half, start, pin.y + half)
    if angle == 270:  # pin on the top edge, name runs down
        start = pin.y - pin.length - offset
        return (pin.x - half, start - span, pin.x + half, start)
    if angle == 90:  # pin on the bottom edge, name runs up
        start = pin.y + pin.length + offset
        return (pin.x - half, start, pin.x + half, start + span)
    return None


def _pins_of(symbol: list[Any]) -> tuple[list[_SymbolPin], list[str]]:
    """Collect pins from the unit sub-symbols; also return sub-symbol names."""
    pins: list[_SymbolPin] = []
    unit_names: list[str] = []
    for unit in children(symbol, "symbol"):
        unit_name = str(unit[1]) if len(unit) > 1 else ""
        unit_names.append(unit_name)
        parts = unit_name.rsplit("_", 2)
        unit_number = int(parts[1]) if len(parts) == 3 and parts[1].isdigit() else 0
        for pin in children(unit, "pin"):
            at = first_child(pin, "at") or []
            length_node = first_child(pin, "length")
            name_node, number_node = first_child(pin, "name"), first_child(pin, "number")
            pins.append(
                _SymbolPin(
                    unit=unit_number,
                    number=str(number_node[1]) if number_node and len(number_node) > 1 else "",
                    name=str(name_node[1]) if name_node and len(name_node) > 1 else "",
                    type=str(pin[1]) if len(pin) > 1 else "",
                    x=as_float(at[1]) if len(at) > 1 else None,
                    y=as_float(at[2]) if len(at) > 2 else None,
                    angle=as_float(at[3]) if len(at) > 3 else None,
                    length=as_float(length_node[1]) if length_node and len(length_node) > 1 else None,
                    alternates=tuple(str(alt[1]) for alt in children(pin, "alternate") if len(alt) > 1),
                )
            )
    return pins, unit_names


def _on_grid(value: float | None) -> bool:
    if value is None:
        return False
    steps = value / GRID
    return abs(steps - round(steps)) < _EPS


def check_symbol(spec: PartSpec, text: str, *, expected_footprint: str | None = None) -> list[Finding]:
    try:
        tree = parse_sexpr(text)
    except ValueError as exc:
        return [Finding("symbol.unparseable", FAIL, f"the symbol library text does not parse: {exc}.")]
    if len(tree) != 1 or not isinstance(tree[0], list) or not tree[0] or tree[0][0] != "kicad_symbol_lib":
        return [Finding("symbol.not_a_library", FAIL, "the file must contain exactly one (kicad_symbol_lib ...).")]
    symbols = [node for node in children(tree[0], "symbol") if len(node) > 1 and node[1] == spec.mpn]
    if len(symbols) != 1:
        return [
            Finding(
                "symbol.name_mismatch",
                FAIL,
                f"expected exactly one top-level symbol named {spec.mpn!r}, found {len(symbols)}.",
                expected=spec.mpn,
                actual=len(symbols),
            )
        ]

    pins, _ = _pins_of(symbols[0])
    findings: list[Finding] = []
    if expected_footprint is not None:
        actual_fp = ""
        for prop in children(symbols[0], "property"):
            if len(prop) > 2 and prop[1] == "Footprint":
                actual_fp = str(prop[2])
        if actual_fp != expected_footprint:
            findings.append(
                Finding(
                    "symbol.footprint_mismatch",
                    FAIL,
                    f"the symbol's Footprint field is {actual_fp!r}; it should be {expected_footprint!r} "
                    "so KiCad assigns the generated footprint.",
                    expected=expected_footprint,
                    actual=actual_fp,
                )
            )
    by_number: dict[str, list[_SymbolPin]] = {}
    for pin in pins:
        by_number.setdefault(pin.number, []).append(pin)

    for number, group in sorted(by_number.items()):
        if len(group) > 1:
            findings.append(
                Finding(
                    "symbol.pin_duplicate",
                    FAIL,
                    f"pin number {number!r} appears {len(group)} times in the symbol.",
                    path=f"pin {number}",
                    actual=len(group),
                )
            )

    spec_numbers = {pin.number for pin in spec.pins}
    for number in sorted(spec_numbers - set(by_number)):
        findings.append(
            Finding(
                "symbol.pin_missing",
                FAIL,
                f"pin {number!r} is in the PartSpec but not in the symbol.",
                path=f"pin {number}",
            )
        )
    for number in sorted(set(by_number) - spec_numbers):
        findings.append(
            Finding(
                "symbol.pin_extra",
                FAIL,
                f"pin {number!r} is in the symbol but not in the PartSpec.",
                path=f"pin {number}",
            )
        )

    for spec_pin in spec.pins:
        found = by_number.get(spec_pin.number)
        if not found:
            continue
        actual = found[0]
        if (actual.name, actual.type) != (spec_pin.name, spec_pin.electrical_type):
            findings.append(
                Finding(
                    "symbol.pin_mismatch",
                    FAIL,
                    f"pin {spec_pin.number!r} differs from the PartSpec (name or electrical type).",
                    path=f"pin {spec_pin.number}",
                    expected={"name": spec_pin.name, "type": spec_pin.electrical_type},
                    actual={"name": actual.name, "type": actual.type},
                )
            )
        if set(actual.alternates) != set(spec_pin.alt_names):
            findings.append(
                Finding(
                    "symbol.alt_mismatch",
                    FAIL,
                    f"pin {spec_pin.number!r} alternate functions differ from the PartSpec alt_names.",
                    path=f"pin {spec_pin.number}",
                    expected=sorted(spec_pin.alt_names),
                    actual=sorted(actual.alternates),
                )
            )

    # Units must follow the groups: same group -> same unit, different groups -> different units.
    unit_of = {number: group[0].unit for number, group in by_number.items()}
    group_units: dict[str | None, set[int]] = {}
    for spec_pin in spec.pins:
        if spec_pin.number in unit_of:
            group_units.setdefault(spec_pin.group, set()).add(unit_of[spec_pin.number])
    for spec_group, units in group_units.items():
        if len(units) > 1:
            findings.append(
                Finding(
                    "symbol.unit_mismatch",
                    FAIL,
                    f"pins of group {spec_group!r} are split across units {sorted(units)}; one group is one unit.",
                    path=f"group {spec_group}",
                    actual=sorted(units),
                )
            )
    unit_groups_seen = Counter(next(iter(units)) for units in group_units.values() if len(units) == 1)
    for unit, count in sorted(unit_groups_seen.items()):
        if count > 1:
            findings.append(
                Finding(
                    "symbol.unit_mismatch",
                    FAIL,
                    f"unit {unit} holds pins from {count} different groups; each group is its own unit.",
                    path=f"unit {unit}",
                    actual=count,
                )
            )

    seen_positions: dict[tuple[int, float, float], str] = {}
    for pin in pins:
        if not (_on_grid(pin.x) and _on_grid(pin.y)):
            findings.append(
                Finding(
                    "symbol.off_grid",
                    FAIL,
                    f"pin {pin.number!r} at ({pin.x}, {pin.y}) is not on the {GRID} mm grid; "
                    "off-grid pins cannot be connected reliably in KiCad.",
                    path=f"pin {pin.number}",
                    actual=[pin.x, pin.y],
                )
            )
            continue
        assert pin.x is not None and pin.y is not None
        key = (pin.unit, round(pin.x, 4), round(pin.y, 4))
        if key in seen_positions:
            findings.append(
                Finding(
                    "symbol.pin_overlap",
                    FAIL,
                    f"pins {seen_positions[key]!r} and {pin.number!r} sit at the same position in unit {pin.unit}.",
                    path=f"pin {pin.number}",
                    actual=[pin.x, pin.y],
                )
            )
        else:
            seen_positions[key] = pin.number

    offset = _name_offset(symbols[0])
    boxes: dict[int, list[tuple[_SymbolPin, tuple[float, float, float, float]]]] = {}
    for pin in pins:
        box = _name_box(pin, offset)
        if box is not None:
            boxes.setdefault(pin.unit, []).append((pin, box))
    for unit, entries in sorted(boxes.items()):
        for index, (first, a) in enumerate(entries):
            for second, b in entries[index + 1 :]:
                if a[0] < b[2] - _EPS and b[0] < a[2] - _EPS and a[1] < b[3] - _EPS and b[1] < a[3] - _EPS:
                    findings.append(
                        Finding(
                            "symbol.name_overlap",
                            FAIL,
                            f"the names of pins {first.number!r} and {second.number!r} overlap in unit {unit}; "
                            "make the body larger or move a pin to another side.",
                            path=f"pin {first.number}",
                            actual=[first.name, second.name],
                        )
                    )
    return findings
