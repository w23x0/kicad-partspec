"""Artifact-layer checks: does a ``.kicad_mod`` text agree with the PartSpec?

The text is parsed again from scratch.  Pad geometry is compared with the
datasheet land pattern, and against the package dimensions to confirm the pads
actually reach the leads; silkscreen and courtyard are checked against the pads.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise
from typing import Any

from partspec.findings import FAIL, WARN, Finding
from partspec.gen.footprint import DUAL_FAMILIES, dim_value
from partspec.sexpr import as_float, children, first_child, parse_sexpr
from partspec.spec.model import PartSpec

_TOL = 0.005  # mm, tolerance when comparing pad geometry with the datasheet
COURTYARD_MIN = 0.25 - 0.001
SILK_CLEARANCE_FAIL = 0.15
PAD_GAP_WARN = 0.1
_SILK_HALF_WIDTH = 0.06  # the marker polygon is drawn with a 0.12 mm stroke


@dataclass(frozen=True)
class _Pad:
    number: str
    x: float
    y: float
    w: float
    h: float

    @property
    def box(self) -> tuple[float, float, float, float]:
        return (self.x - self.w / 2, self.y - self.h / 2, self.x + self.w / 2, self.y + self.h / 2)


Point = tuple[float, float]


def _num(node: Any, index: int) -> float | None:
    return as_float(node[index]) if isinstance(node, list) and len(node) > index else None


def _pads(fp: list[Any]) -> list[_Pad]:
    pads: list[_Pad] = []
    for node in children(fp, "pad"):
        at, size = first_child(node, "at"), first_child(node, "size")
        x, y, w, h = _num(at, 1), _num(at, 2), _num(size, 1), _num(size, 2)
        if None in (x, y, w, h) or len(node) < 2:
            continue
        assert x is not None and y is not None and w is not None and h is not None
        pads.append(_Pad(str(node[1]), x, y, w, h))
    return pads


def _segments(fp: list[Any], layer: str) -> list[tuple[Point, Point, float]]:
    found: list[tuple[Point, Point, float]] = []
    for node in children(fp, "fp_line"):
        if (first_child(node, "layer") or [None, None])[1] != layer:
            continue
        start, end, stroke = first_child(node, "start"), first_child(node, "end"), first_child(node, "stroke")
        x0, y0, x1, y1 = _num(start, 1), _num(start, 2), _num(end, 1), _num(end, 2)
        if None in (x0, y0, x1, y1):
            continue
        assert x0 is not None and y0 is not None and x1 is not None and y1 is not None
        found.append(((x0, y0), (x1, y1), _num(first_child(stroke, "width"), 1) or 0.0 if stroke else 0.0))
    return found


def _polys(fp: list[Any], layer: str) -> list[list[Point]]:
    found: list[list[Point]] = []
    for node in children(fp, "fp_poly"):
        if (first_child(node, "layer") or [None, None])[1] != layer:
            continue
        pts = [(_num(p, 1), _num(p, 2)) for p in children(first_child(node, "pts") or [], "xy")]
        found.append([(x, y) for x, y in pts if x is not None and y is not None])
    return found


def _seg_dist(p: Point, q: Point, r: Point, s: Point) -> float:
    """Distance between segments pq and rs."""

    def orient(a: Point, b: Point, c: Point) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    if orient(p, q, r) * orient(p, q, s) < 0 and orient(r, s, p) * orient(r, s, q) < 0:
        return 0.0

    def point_seg(pt: Point, a: Point, b: Point) -> float:
        dx, dy = b[0] - a[0], b[1] - a[1]
        length2 = dx * dx + dy * dy
        t = 0.0 if length2 == 0 else max(0.0, min(1.0, ((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / length2))
        return math.hypot(pt[0] - (a[0] + t * dx), pt[1] - (a[1] + t * dy))

    return min(point_seg(p, r, s), point_seg(q, r, s), point_seg(r, p, q), point_seg(s, p, q))


def _seg_rect_dist(a: Point, b: Point, box: tuple[float, float, float, float]) -> float:
    x0, y0, x1, y1 = box

    def inside(pt: Point) -> bool:
        return x0 <= pt[0] <= x1 and y0 <= pt[1] <= y1

    if inside(a) or inside(b):
        return 0.0
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return min(_seg_dist(a, b, corners[i], corners[(i + 1) % 4]) for i in range(4))


def _dim(spec: PartSpec, name: str) -> float | None:
    return dim_value(spec.package.dimensions.get(name))


def check_footprint(spec: PartSpec, text: str) -> list[Finding]:
    try:
        tree = parse_sexpr(text)
    except ValueError as exc:
        return [Finding("footprint.unparseable", FAIL, f"the footprint text does not parse: {exc}.")]
    if len(tree) != 1 or not isinstance(tree[0], list) or not tree[0] or tree[0][0] != "footprint":
        return [Finding("footprint.not_a_footprint", FAIL, "the file must contain exactly one (footprint ...).")]
    fp = tree[0]
    pads = _pads(fp)
    findings: list[Finding] = []

    # --- pad numbers against the spec pins
    numbers = [pad.number for pad in pads]
    for number in sorted({n for n in numbers if numbers.count(n) > 1}):
        findings.append(
            Finding(
                "footprint.pad_duplicate", FAIL, f"pad number {number!r} appears more than once.", path=f"pad {number}"
            )
        )
    spec_numbers = {pin.number for pin in spec.pins}
    for number in sorted(spec_numbers - set(numbers)):
        findings.append(
            Finding("footprint.pad_missing", FAIL, f"pin {number!r} has no pad in the footprint.", path=f"pad {number}")
        )
    for number in sorted(set(numbers) - spec_numbers):
        findings.append(
            Finding(
                "footprint.pad_extra",
                FAIL,
                f"pad {number!r} does not correspond to a PartSpec pin.",
                path=f"pad {number}",
            )
        )

    ep_number = str(spec.package.pin_count + 1) if spec.package.exposed_pad else None
    ring = [pad for pad in pads if pad.number != ep_number]
    pitch = _dim(spec, "pitch")

    # --- pitch between neighbours along each edge of the pad ring
    if pitch is not None and ring:
        half = max(max(abs(pad.x), abs(pad.y)) for pad in ring)
        for axis in (0, 1):
            lines: dict[float, list[float]] = {}
            for pad in ring:
                across, along = (pad.x, pad.y) if axis == 0 else (pad.y, pad.x)
                # Pads on the perpendicular edge are not neighbours along this one.
                if abs(along) < half - 1e-6:
                    lines.setdefault(round(across, 3), []).append(along)
            for positions in lines.values():
                positions.sort()
                for a, b in pairwise(positions):
                    if abs((b - a) - pitch) > _TOL:
                        findings.append(
                            Finding(
                                "footprint.pitch",
                                FAIL,
                                f"neighbouring pads are {b - a:.3f} mm apart but the datasheet pitch is {pitch} mm.",
                                expected=pitch,
                                actual=round(b - a, 4),
                            )
                        )

    # --- pad geometry against the datasheet land pattern
    length, width, span = _dim(spec, "land_pad_length"), _dim(spec, "land_pad_width"), _dim(spec, "land_span")
    if length is not None and width is not None and span is not None:
        for pad in ring:
            sizes = sorted((pad.w, pad.h))
            if abs(sizes[0] - min(length, width)) > _TOL or abs(sizes[1] - max(length, width)) > _TOL:
                findings.append(
                    Finding(
                        "footprint.land_mismatch",
                        FAIL,
                        f"pad {pad.number!r} is {pad.w}x{pad.h} mm but the datasheet land pattern is {length}x{width} mm.",
                        path=f"pad {pad.number}",
                        expected=[length, width],
                        actual=[pad.w, pad.h],
                    )
                )
            if abs(max(abs(pad.x), abs(pad.y)) - span / 2) > _TOL:
                findings.append(
                    Finding(
                        "footprint.land_mismatch",
                        FAIL,
                        f"pad {pad.number!r} centre is {max(abs(pad.x), abs(pad.y)) * 2:.3f} mm across, "
                        f"but the datasheet land span is {span} mm.",
                        path=f"pad {pad.number}",
                        expected=span,
                        actual=round(max(abs(pad.x), abs(pad.y)) * 2, 4),
                    )
                )
    ep_size = _dim(spec, "land_ep_size")
    if ep_number is not None and ep_size is not None:
        for pad in pads:
            if pad.number == ep_number and (
                abs(pad.w - ep_size) > _TOL or abs(pad.h - ep_size) > _TOL or abs(pad.x) > _TOL or abs(pad.y) > _TOL
            ):
                findings.append(
                    Finding(
                        "footprint.ep_mismatch",
                        FAIL,
                        f"the exposed pad must be {ep_size}x{ep_size} mm centred on the origin.",
                        path=f"pad {pad.number}",
                        expected=ep_size,
                        actual=[pad.w, pad.h, pad.x, pad.y],
                    )
                )

    # --- do the pads reach the leads? (nominal package dimensions)
    findings += _lead_coverage(spec, ring)

    # --- pads must not touch each other
    for index, first in enumerate(pads):
        for second in pads[index + 1 :]:
            ax0, ay0, ax1, ay1 = first.box
            bx0, by0, bx1, by1 = second.box
            gap = max(bx0 - ax1, ax0 - bx1, by0 - ay1, ay0 - by1)
            if gap < 0:
                findings.append(
                    Finding(
                        "footprint.pad_overlap",
                        FAIL,
                        f"pads {first.number!r} and {second.number!r} overlap.",
                        path=f"pad {first.number}",
                    )
                )
            elif gap < PAD_GAP_WARN:
                findings.append(
                    Finding(
                        "footprint.pad_gap",
                        WARN,
                        f"pads {first.number!r} and {second.number!r} are only {gap:.3f} mm apart.",
                        path=f"pad {first.number}",
                        actual=round(gap, 4),
                    )
                )

    findings += _courtyard(fp, pads)
    findings += _silkscreen(fp, pads)
    return findings


def _lead_coverage(spec: PartSpec, ring: list[_Pad]) -> list[Finding]:
    """Compare pad edges with the nominal lead tip, heel and width from the package drawing."""
    if not ring:
        return []
    lead_length, lead_width = _dim(spec, "lead_length"), _dim(spec, "lead_width")
    if spec.package.family.upper() in DUAL_FAMILIES:
        reach = _dim(spec, "overall_width") or _dim(spec, "body_width")
    else:
        reach = _dim(spec, "overall_length") or _dim(spec, "body_length")
    if reach is None or lead_length is None or lead_width is None:
        return []
    tip = reach / 2
    heel = tip - lead_length
    findings: list[Finding] = []
    reported: set[str] = set()
    for pad in ring:
        radial, along = (abs(pad.x), pad.w) if abs(pad.x) >= abs(pad.y) else (abs(pad.y), pad.h)
        across = pad.h if abs(pad.x) >= abs(pad.y) else pad.w
        outer, inner = radial + along / 2, radial - along / 2
        checks = (
            ("toe", outer - tip, "the pad stops short of the lead tip"),
            ("heel", heel - inner, "the pad does not reach the lead's heel"),
            ("side", (across - lead_width) / 2, "the pad is narrower than the lead"),
        )
        for label, margin, meaning in checks:
            if margin < -_TOL and label not in reported:
                reported.add(label)
                findings.append(
                    Finding(
                        f"footprint.{label}_coverage",
                        FAIL,
                        f"{meaning} (pad {pad.number!r}, {label} margin {margin:.3f} mm); "
                        "recheck the land pattern and lead dimensions.",
                        path=f"pad {pad.number}",
                        actual=round(margin, 4),
                    )
                )
    return findings


def _courtyard(fp: list[Any], pads: list[_Pad]) -> list[Finding]:
    lines = _segments(fp, "F.CrtYd")
    if not lines:
        return [Finding("footprint.courtyard_missing", FAIL, "the footprint has no F.CrtYd courtyard.")]
    xs = [pt[0] for a, b, _ in lines for pt in (a, b)]
    ys = [pt[1] for a, b, _ in lines for pt in (a, b)]
    left, right, top, bottom = min(xs), max(xs), min(ys), max(ys)
    if not pads:
        return []
    gaps = [
        min(pad.box[0] for pad in pads) - left,
        right - max(pad.box[2] for pad in pads),
        min(pad.box[1] for pad in pads) - top,
        bottom - max(pad.box[3] for pad in pads),
    ]
    if min(gaps) < COURTYARD_MIN:
        return [
            Finding(
                "footprint.courtyard_small",
                FAIL,
                f"the courtyard is only {min(gaps):.3f} mm from the pads; keep at least 0.25 mm.",
                actual=round(min(gaps), 4),
            )
        ]
    return []


def _silkscreen(fp: list[Any], pads: list[_Pad]) -> list[Finding]:
    findings: list[Finding] = []
    worst = math.inf
    for a, b, width in _segments(fp, "F.SilkS"):
        for pad in pads:
            worst = min(worst, _seg_rect_dist(a, b, pad.box) - width / 2)
    for poly in _polys(fp, "F.SilkS"):
        for index, a in enumerate(poly):
            b = poly[(index + 1) % len(poly)]
            for pad in pads:
                worst = min(worst, _seg_rect_dist(a, b, pad.box) - _SILK_HALF_WIDTH)
    if worst < SILK_CLEARANCE_FAIL:
        findings.append(
            Finding(
                "footprint.silk_on_pad",
                FAIL,
                f"silkscreen comes within {max(worst, 0):.3f} mm of a pad; keep it at least "
                f"{SILK_CLEARANCE_FAIL} mm away (0.2 mm is the KiCad library convention).",
                actual=round(worst, 4),
            )
        )
    return findings
