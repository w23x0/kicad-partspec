"""Generate a KiCad footprint (``.kicad_mod``) from a PartSpec.

Pad geometry comes straight from the datasheet's example land pattern (the
``land_*`` dimensions), so every number is traceable to a quoted datasheet
page.  Two package layouts are supported: dual-row (SOIC, TSSOP, ...) and
square quad (QFN, QFP, ...), each with an optional exposed pad.  Specs without
a land pattern are skipped with a reason rather than guessed at.

Coordinates follow KiCad: X to the right, Y downward; pin 1 is the top-left
pad of the left column; numbering runs counter-clockwise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from partspec.sexpr import Atom, write_sexpr
from partspec.spec.model import Dimension, PartSpec

FORMAT_VERSION = "20241229"
DUAL_FAMILIES = frozenset({"SOIC", "SOP", "SSOP", "TSSOP", "MSOP", "VSSOP"})
QUAD_FAMILIES = frozenset({"QFN", "VQFN", "WQFN", "UQFN", "QFP", "TQFP", "LQFP"})
_NAME_FAMILY = {"VQFN": "QFN", "WQFN": "QFN", "UQFN": "QFN"}

SILK_WIDTH = 0.12
FAB_WIDTH = 0.1
COURTYARD_WIDTH = 0.05
COURTYARD_MARGIN = 0.25
SILK_CLEARANCE = 0.2  # edge of silkscreen line to edge of pad
BRACKET_LENGTH = 1.0
ROUNDRECT_RATIO = 0.25
REQUIRED = ("pitch", "land_pad_length", "land_pad_width", "land_span", "body_length", "body_width")


def dim_value(dim: Dimension | None) -> float | None:
    """The nominal value of a dimension, or the middle of its min/max range."""
    if dim is None:
        return None
    if dim.nom is not None:
        return dim.nom
    if dim.min is not None and dim.max is not None:
        return (dim.min + dim.max) / 2
    return dim.max if dim.max is not None else dim.min


def _dim(spec: PartSpec, name: str) -> float | None:
    return dim_value(spec.package.dimensions.get(name))


def skip_reason(spec: PartSpec) -> str | None:
    """Why no footprint can be generated for this spec, or None when one can."""
    family = spec.package.family.upper()
    count = spec.package.pin_count
    if family in DUAL_FAMILIES:
        if count % 2:
            return f"a dual-row {family} package needs an even pin_count, got {count}"
    elif family in QUAD_FAMILIES:
        if count % 4:
            return f"a quad {family} package needs a pin_count divisible by 4, got {count}"
    else:
        return f"package family {spec.package.family!r} is not supported (supported: dual-row and quad packages)"
    missing = [name for name in REQUIRED if _dim(spec, name) is None]
    if spec.package.exposed_pad and _dim(spec, "land_ep_size") is None:
        missing.append("land_ep_size")
    if missing:
        return (
            "the datasheet land pattern is incomplete; add these dimensions with a source: "
            + ", ".join(missing)
            + " (footprints are generated from the datasheet's example land pattern, not computed)"
        )
    if family in QUAD_FAMILIES:
        length, width = _dim(spec, "body_length"), _dim(spec, "body_width")
        assert length is not None and width is not None
        if abs(length - width) > 0.1:
            return "non-square quad bodies are not supported (one land_span is used for both axes)"
    return None


@dataclass(frozen=True)
class PadSpec:
    number: str
    x: float
    y: float
    width: float
    height: float
    shape: str  # "roundrect" or "rect"


def _r(value: float) -> float:
    return round(value + 0.0, 4)  # "+ 0.0" turns -0.0 into 0.0


def compute_pads(spec: PartSpec) -> list[PadSpec]:
    """Pad list for a supported spec (call ``skip_reason`` first)."""
    count = spec.package.pin_count
    pitch = _dim(spec, "pitch")
    length, width = _dim(spec, "land_pad_length"), _dim(spec, "land_pad_width")
    span = _dim(spec, "land_span")
    assert pitch is not None and length is not None and width is not None and span is not None
    half = span / 2
    pads: list[PadSpec] = []
    if spec.package.family.upper() in DUAL_FAMILIES:
        per_side = count // 2
        offsets = [(index - (per_side - 1) / 2) * pitch for index in range(per_side)]
        for index, y in enumerate(offsets):
            pads.append(PadSpec(str(index + 1), _r(-half), _r(y), length, width, "roundrect"))
        for index, y in enumerate(reversed(offsets)):
            pads.append(PadSpec(str(per_side + index + 1), _r(half), _r(y), length, width, "roundrect"))
    else:
        per_side = count // 4
        offsets = [(index - (per_side - 1) / 2) * pitch for index in range(per_side)]
        for index, y in enumerate(offsets):  # left, top to bottom
            pads.append(PadSpec(str(index + 1), _r(-half), _r(y), length, width, "roundrect"))
        for index, x in enumerate(offsets):  # bottom, left to right
            pads.append(PadSpec(str(per_side + index + 1), _r(x), _r(half), width, length, "roundrect"))
        for index, y in enumerate(reversed(offsets)):  # right, bottom to top
            pads.append(PadSpec(str(2 * per_side + index + 1), _r(half), _r(y), length, width, "roundrect"))
        for index, x in enumerate(reversed(offsets)):  # top, right to left
            pads.append(PadSpec(str(3 * per_side + index + 1), _r(x), _r(-half), width, length, "roundrect"))
    if spec.package.exposed_pad:
        ep = _dim(spec, "land_ep_size")
        assert ep is not None
        pads.append(PadSpec(str(count + 1), 0.0, 0.0, ep, ep, "rect"))
    return pads


def _fmt(value: float) -> str:
    return f"{round(value, 2):g}"


def footprint_name(spec: PartSpec) -> str:
    family = spec.package.family.upper()
    family = _NAME_FAMILY.get(family, family)
    count = spec.package.pin_count
    pitch = _dim(spec, "pitch")
    length, width = _dim(spec, "body_length"), _dim(spec, "body_width")
    assert pitch is not None and length is not None and width is not None
    if spec.package.family.upper() in DUAL_FAMILIES:
        return f"{family}-{count}_{width:.1f}x{length:.1f}mm_P{_fmt(pitch)}mm"
    if spec.package.exposed_pad:
        ep = _dim(spec, "land_ep_size")
        assert ep is not None
        return f"{family}-{count}-1EP_{_fmt(width)}x{_fmt(length)}mm_P{_fmt(pitch)}mm_EP{_fmt(ep)}x{_fmt(ep)}mm"
    return f"{family}-{count}_{_fmt(width)}x{_fmt(length)}mm_P{_fmt(pitch)}mm"


# --------------------------------------------------------------------------- silkscreen


Segment = tuple[float, float, float, float]  # x0, y0, x1, y1 (axis-aligned)


def _inflate(pad: PadSpec, margin: float) -> tuple[float, float, float, float]:
    return (
        pad.x - pad.width / 2 - margin,
        pad.y - pad.height / 2 - margin,
        pad.x + pad.width / 2 + margin,
        pad.y + pad.height / 2 + margin,
    )


def _clip(segment: Segment, pads: list[PadSpec], margin: float) -> list[Segment]:
    """Remove the parts of an axis-aligned segment that come within ``margin`` of a pad."""
    x0, y0, x1, y1 = segment
    horizontal = abs(y1 - y0) < 1e-9
    fixed = y0 if horizontal else x0
    lo, hi = sorted((x0, x1) if horizontal else (y0, y1))
    pieces = [(lo, hi)]
    for pad in pads:
        rx0, ry0, rx1, ry1 = _inflate(pad, margin)
        near, start, end = (ry0 < fixed < ry1, rx0, rx1) if horizontal else (rx0 < fixed < rx1, ry0, ry1)
        if not near:
            continue
        cut: list[tuple[float, float]] = []
        for a, b in pieces:
            if end <= a or start >= b:
                cut.append((a, b))
                continue
            if start > a:
                cut.append((a, start))
            if end < b:
                cut.append((end, b))
        pieces = cut
    if horizontal:
        return [(a, fixed, b, fixed) for a, b in pieces if b - a > 0.05]
    return [(fixed, a, fixed, b) for a, b in pieces if b - a > 0.05]


def _silk_segments(spec: PartSpec, pads: list[PadSpec]) -> list[Segment]:
    body_w, body_l = _dim(spec, "body_width"), _dim(spec, "body_length")
    assert body_w is not None and body_l is not None
    hw, hl = body_w / 2 + SILK_WIDTH, body_l / 2 + SILK_WIDTH
    margin = SILK_CLEARANCE + SILK_WIDTH / 2
    signal = [pad for pad in pads if pad.shape != "rect" or pad.x or pad.y]
    if spec.package.family.upper() in DUAL_FAMILIES:
        raw: list[Segment] = [(-hw, -hl, hw, -hl), (-hw, hl, hw, hl)]
    else:  # corner brackets
        n = BRACKET_LENGTH
        raw = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                raw.append((sx * hw, sy * hl, sx * (hw - n), sy * hl))
                raw.append((sx * hw, sy * hl, sx * hw, sy * (hl - n)))
    out: list[Segment] = []
    for segment in raw:
        out.extend(_clip(segment, signal, margin))
    return out


# --------------------------------------------------------------------------- tree


def _stroke(width: float) -> list[Any]:
    return [Atom("stroke"), [Atom("width"), width], [Atom("type"), Atom("solid")]]


def _line(seg: Segment, width: float, layer: str) -> list[Any]:
    x0, y0, x1, y1 = seg
    return [
        Atom("fp_line"),
        [Atom("start"), _r(x0), _r(y0)],
        [Atom("end"), _r(x1), _r(y1)],
        _stroke(width),
        [Atom("layer"), layer],
    ]


def _text_effects() -> list[Any]:
    return [Atom("effects"), [Atom("font"), [Atom("size"), 1, 1], [Atom("thickness"), 0.15]]]


def _pad_node(pad: PadSpec) -> list[Any]:
    node: list[Any] = [
        Atom("pad"),
        pad.number,
        Atom("smd"),
        Atom(pad.shape),
        [Atom("at"), pad.x, pad.y],
        [Atom("size"), _r(pad.width), _r(pad.height)],
        [Atom("layers"), "F.Cu", "F.Mask", "F.Paste"],
    ]
    if pad.shape == "roundrect":
        node.append([Atom("roundrect_rratio"), ROUNDRECT_RATIO])
    return node


def _round_out(value: float, up: bool) -> float:
    scaled = value * 100
    return (math.ceil(scaled - 1e-6) if up else math.floor(scaled + 1e-6)) / 100


def build_footprint(spec: PartSpec, name: str | None = None) -> list[Any]:
    """Build the ``(footprint ...)`` tree (call ``skip_reason`` first)."""
    name = name or footprint_name(spec)
    body_w, body_l = _dim(spec, "body_width"), _dim(spec, "body_length")
    assert body_w is not None and body_l is not None
    pads = compute_pads(spec)
    silk = _silk_segments(spec, pads)

    # Fab outline with a chamfer at pin 1 (top-left corner).
    hw, hl = body_w / 2, body_l / 2
    cut = min(1.0, body_w / 4, body_l / 4)
    outline: list[Segment] = [
        (-hw + cut, -hl, hw, -hl),
        (hw, -hl, hw, hl),
        (hw, hl, -hw, hl),
        (-hw, hl, -hw, -hl + cut),
        (-hw, -hl + cut, -hw + cut, -hl),
    ]

    # Pin 1 marker: a small filled triangle outside the pad column, pointing at pad 1.
    pin1 = pads[0]
    outer = abs(pin1.x) + pin1.width / 2
    tip_x = -(outer + SILK_CLEARANCE + SILK_WIDTH / 2 + 0.05)
    marker = [(tip_x, pin1.y), (tip_x - 0.5, pin1.y - 0.3), (tip_x - 0.5, pin1.y + 0.3)]

    xs = [p.x - p.width / 2 for p in pads] + [p.x + p.width / 2 for p in pads] + [-hw, hw]
    ys = [p.y - p.height / 2 for p in pads] + [p.y + p.height / 2 for p in pads] + [-hl, hl]
    for x0, y0, x1, y1 in silk:
        xs += [x0, x1]
        ys += [y0, y1]
    xs += [pt[0] for pt in marker]
    ys += [pt[1] for pt in marker]
    left = _round_out(min(xs) - COURTYARD_MARGIN, up=False)
    right = _round_out(max(xs) + COURTYARD_MARGIN, up=True)
    top = _round_out(min(ys) - COURTYARD_MARGIN, up=False)
    bottom = _round_out(max(ys) + COURTYARD_MARGIN, up=True)
    courtyard: list[Segment] = [
        (left, top, right, top),
        (right, top, right, bottom),
        (right, bottom, left, bottom),
        (left, bottom, left, top),
    ]

    fab_size = round(min(1.0, max(0.3, min(body_w, body_l) / 4)), 2)
    family = spec.package.family
    description = f"{family}, {spec.package.pin_count} Pin ({spec.manufacturer} {spec.mpn} datasheet land pattern)"
    node: list[Any] = [
        Atom("footprint"),
        name,
        [Atom("version"), Atom(FORMAT_VERSION)],
        [Atom("generator"), "partspec"],
        [Atom("generator_version"), "0.0.1"],
        [Atom("layer"), "F.Cu"],
        [Atom("descr"), description],
        [Atom("tags"), family],
        [
            Atom("property"),
            "Reference",
            "REF**",
            [Atom("at"), 0, _r(top - 1)],
            [Atom("layer"), "F.SilkS"],
            _text_effects(),
        ],
        [Atom("property"), "Value", name, [Atom("at"), 0, _r(bottom + 1)], [Atom("layer"), "F.Fab"], _text_effects()],
        [Atom("attr"), Atom("smd")],
    ]
    node += [_line(seg, SILK_WIDTH, "F.SilkS") for seg in silk]
    node.append(
        [
            Atom("fp_poly"),
            [Atom("pts"), *[[Atom("xy"), _r(px), _r(py)] for px, py in marker]],
            _stroke(SILK_WIDTH),
            [Atom("fill"), Atom("yes")],
            [Atom("layer"), "F.SilkS"],
        ]
    )
    node += [_line(seg, COURTYARD_WIDTH, "F.CrtYd") for seg in courtyard]
    node += [_line(seg, FAB_WIDTH, "F.Fab") for seg in outline]
    node.append(
        [
            Atom("fp_text"),
            Atom("user"),
            "${REFERENCE}",
            [Atom("at"), 0, 0],
            [Atom("layer"), "F.Fab"],
            [Atom("effects"), [Atom("font"), [Atom("size"), fab_size, fab_size], [Atom("thickness"), 0.15]]],
        ]
    )
    node += [_pad_node(pad) for pad in pads]
    node.append([Atom("embedded_fonts"), Atom("no")])
    return node


def render_footprint(spec: PartSpec, name: str | None = None) -> str:
    return write_sexpr(build_footprint(spec, name))
