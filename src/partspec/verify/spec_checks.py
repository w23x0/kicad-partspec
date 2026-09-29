"""Spec-layer checks: internal consistency of a loaded PartSpec.

Each check returns findings and never raises; ``message`` tells the agent what
to change.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable

from partspec.findings import FAIL, WARN, Finding
from partspec.spec.model import ELECTRICAL_TYPES, STATUSES, PartSpec, Source


def _source_problem(source: Source | None) -> str | None:
    if source is None:
        return "has no source"
    if source.page < 1:
        return "has source.page < 1"
    if not source.quote.strip():
        return "has an empty source.quote"
    return None


def check_provenance(spec: PartSpec) -> list[Finding]:
    """Every pin and dimension must cite a datasheet page and a quote."""
    findings: list[Finding] = []
    items = [(f"pins[{i}]", pin.source) for i, pin in enumerate(spec.pins)]
    items += [(f"package.dimensions.{name}", dim.source) for name, dim in spec.package.dimensions.items()]
    for path, source in items:
        problem = _source_problem(source)
        if problem:
            findings.append(
                Finding(
                    "prov.missing",
                    FAIL,
                    f"{path} {problem}; cite the datasheet page number and quote the table row or figure text.",
                    path=path,
                )
            )
    return findings


def check_pin_count(spec: PartSpec) -> list[Finding]:
    expected = spec.package.pin_count + (1 if spec.package.exposed_pad else 0)
    if len(spec.pins) == expected:
        return []
    detail = " (package.pin_count plus one exposed pad)" if spec.package.exposed_pad else ""
    return [
        Finding(
            "pins.count_mismatch",
            FAIL,
            f"pins has {len(spec.pins)} entries but the package needs {expected}{detail}; "
            "add the missing pins or correct package.pin_count.",
            path="pins",
            expected=expected,
            actual=len(spec.pins),
        )
    ]


def check_pin_numbers_unique(spec: PartSpec) -> list[Finding]:
    counts = Counter(pin.number for pin in spec.pins)
    return [
        Finding(
            "pins.duplicate_number",
            FAIL,
            f"pin number {number!r} appears {count} times; every physical pin needs a unique number.",
            path="pins",
            actual=count,
        )
        for number, count in sorted(counts.items())
        if count > 1
    ]


def check_electrical_types(spec: PartSpec) -> list[Finding]:
    return [
        Finding(
            "pins.bad_type",
            FAIL,
            f"pins[{i}].electrical_type {pin.electrical_type!r} is not a KiCad pin type; "
            f"use one of: {', '.join(ELECTRICAL_TYPES)}.",
            path=f"pins[{i}].electrical_type",
            expected=list(ELECTRICAL_TYPES),
            actual=pin.electrical_type,
        )
        for i, pin in enumerate(spec.pins)
        if pin.electrical_type not in ELECTRICAL_TYPES
    ]


def check_dimension_order(spec: PartSpec) -> list[Finding]:
    findings: list[Finding] = []
    for name, dim in spec.package.dimensions.items():
        path = f"package.dimensions.{name}"
        values = [
            (label, value)
            for label, value in (("min", dim.min), ("nom", dim.nom), ("max", dim.max))
            if value is not None
        ]
        if not values:
            findings.append(
                Finding("dim.empty", FAIL, f"{path} has no min, nom or max; provide at least one value.", path=path)
            )
            continue
        # A minimum of 0 is legitimate (e.g. a standoff that can sit on the board);
        # nominal and maximum values must be strictly positive.
        if any(value < 0 or (value == 0 and label != "min") for label, value in values):
            findings.append(
                Finding(
                    "dim.non_positive",
                    FAIL,
                    f"{path} has a negative value, or a nom/max of 0; dimensions are in mm, min may be 0.",
                    path=path,
                )
            )
        numbers = [value for _, value in values]
        if numbers != sorted(numbers):
            findings.append(
                Finding(
                    "dim.order",
                    FAIL,
                    f"{path} must satisfy min <= nom <= max; re-read the datasheet table for this dimension.",
                    path=path,
                    actual={label: value for label, value in values},
                )
            )
    return findings


def check_statuses(spec: PartSpec) -> list[Finding]:
    findings: list[Finding] = []
    items = [(f"pins[{i}]", pin.status) for i, pin in enumerate(spec.pins)]
    items += [(f"package.dimensions.{name}", dim.status) for name, dim in spec.package.dimensions.items()]
    for path, status in items:
        if status not in STATUSES:
            findings.append(
                Finding(
                    "status.invalid",
                    FAIL,
                    f"{path}.status {status!r} is invalid; use one of: {', '.join(STATUSES)}.",
                    path=f"{path}.status",
                    expected=list(STATUSES),
                    actual=status,
                )
            )
        elif status == "inferred":
            findings.append(
                Finding(
                    "status.inferred",
                    WARN,
                    f"{path} is inferred, not read from the datasheet; a human should confirm it.",
                    path=f"{path}.status",
                )
            )
    return findings


SPEC_CHECKS: tuple[Callable[[PartSpec], list[Finding]], ...] = (
    check_provenance,
    check_pin_count,
    check_pin_numbers_unique,
    check_electrical_types,
    check_dimension_order,
    check_statuses,
)
