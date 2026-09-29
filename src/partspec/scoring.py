"""Score an extracted PartSpec against a gold PartSpec.

Field-level accuracy says where extraction goes wrong; ``usable_without_edit`` is
the number that matters: would the generated KiCad parts be identical to the
ones built from the gold spec, with every quote confirmed on its datasheet page?
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from partspec.findings import FAIL
from partspec.gen.footprint import compute_pads, skip_reason
from partspec.spec import PartSpec, load_spec
from partspec.verify import verify_spec
from partspec.verify.quotes import check_quotes

DIM_TOL = 0.006  # gold values are written to two decimals
# EN DASH, EM DASH, MINUS SIGN, HYPHEN, NON-BREAKING HYPHEN: datasheets print these where ASCII "-" is meant.
_DASHES = str.maketrans(dict.fromkeys("\u2013\u2014\u2212\u2010\u2011", "-"))


def _norm(text: str) -> str:
    return text.translate(_DASHES).strip()


@dataclass
class Score:
    case: str
    loaded: bool = False
    spec_failures: list[str] = field(default_factory=list)
    package_ok: bool = False
    pins_gold: int = 0
    pins_found: int = 0
    pins_extra: int = 0
    names_ok: int = 0
    types_ok: int = 0
    alts_ok: int = 0
    groups_ok: int = 0
    status_agree: int = 0
    status_under: int = 0  # marked extracted where gold says inferred: the risky direction
    status_over: int = 0  # marked inferred where gold says extracted: conservative
    dims_gold: int = 0
    dims_ok: int = 0
    dims_missing: list[str] = field(default_factory=list)
    dims_wrong: list[str] = field(default_factory=list)
    dims_extra: list[str] = field(default_factory=list)
    quotes_total: int | None = None
    quotes_bad: int | None = None
    symbol_identical: bool = False
    footprint_identical: bool = False
    pin_errors: list[str] = field(default_factory=list)

    @property
    def usable_without_edit(self) -> bool:
        quotes_fine = self.quotes_bad in (0, None)
        return (
            self.loaded
            and not self.spec_failures
            and self.symbol_identical
            and self.footprint_identical
            and quotes_fine
        )

    def to_dict(self) -> dict[str, Any]:
        data = {key: getattr(self, key) for key in self.__dataclass_fields__}
        data["usable_without_edit"] = self.usable_without_edit
        return data


def _pin_key(pin: Any) -> str:
    return str(pin.number)


def _same_dim(gold: Any, other: Any) -> bool:
    for label in ("min", "nom", "max"):
        expected, actual = getattr(gold, label), getattr(other, label)
        if expected is None:
            continue
        if actual is None or abs(actual - expected) > DIM_TOL:
            return False
    return True


def _same_footprint(gold: PartSpec, other: PartSpec) -> bool:
    if (skip_reason(gold) is None) != (skip_reason(other) is None):
        return False
    if skip_reason(gold) is not None:
        return True  # both skipped: nothing to differ
    a, b = compute_pads(gold), compute_pads(other)
    if [p.number for p in a] != [p.number for p in b]:
        return False
    return all(
        p.shape == q.shape
        and all(abs(x - y) <= DIM_TOL for x, y in ((p.x, q.x), (p.y, q.y), (p.width, q.width), (p.height, q.height)))
        for p, q in zip(a, b, strict=True)
    )


def score(case: str, gold_data: Any, extracted_data: Any, pages: list[str] | None = None) -> Score:
    """Compare one extraction with its gold spec. ``pages`` (datasheet page texts) enables the quote check."""
    result = Score(case)
    gold, gold_findings = load_spec(gold_data)
    assert gold is not None, gold_findings
    spec, findings = load_spec(extracted_data)
    result.pins_gold = len(gold.pins)
    result.dims_gold = len(gold.package.dimensions)
    if pages is not None and isinstance(extracted_data, dict):
        found = check_quotes(extracted_data, pages)
        sources = sum(
            1
            for item in (extracted_data.get("pins") or [])
            if isinstance(item, dict) and isinstance(item.get("source"), dict)
        ) + sum(
            1
            for item in ((extracted_data.get("package") or {}).get("dimensions") or {}).values()
            if isinstance(item, dict) and isinstance(item.get("source"), dict)
        )
        result.quotes_total, result.quotes_bad = sources, len(found)
    if spec is None:
        result.spec_failures = [item.id for item in findings]
        result.dims_missing = sorted(gold.package.dimensions)
        return result
    result.loaded = True
    result.spec_failures = sorted({item.id for item in verify_spec(extracted_data) if item.status == FAIL})

    result.package_ok = (
        spec.package.family.upper() == gold.package.family.upper()
        and spec.package.pin_count == gold.package.pin_count
        and spec.package.exposed_pad == gold.package.exposed_pad
    )

    theirs = {_pin_key(pin): pin for pin in spec.pins}
    result.pins_extra = len(set(theirs) - {_pin_key(pin) for pin in gold.pins})
    for pin in gold.pins:
        other = theirs.get(_pin_key(pin))
        if other is None:
            result.pin_errors.append(f"pin {pin.number}: missing")
            continue
        result.pins_found += 1
        problems = []
        if _norm(other.name) == _norm(pin.name):
            result.names_ok += 1
        else:
            problems.append(f"name {other.name!r} != {pin.name!r}")
        if other.electrical_type == pin.electrical_type:
            result.types_ok += 1
        else:
            problems.append(f"type {other.electrical_type} != {pin.electrical_type}")
        if {_norm(a) for a in other.alt_names} == {_norm(a) for a in pin.alt_names}:
            result.alts_ok += 1
        else:
            problems.append(f"alt_names {list(other.alt_names)} != {list(pin.alt_names)}")
        if (other.group or None) == (pin.group or None) or (
            other.group and pin.group and other.group.lower() == pin.group.lower()
        ):
            result.groups_ok += 1
        else:
            problems.append(f"group {other.group!r} != {pin.group!r}")
        if (other.status == "inferred") == (pin.status == "inferred"):
            result.status_agree += 1
        elif pin.status == "inferred":
            result.status_under += 1
        else:
            result.status_over += 1
        if problems:
            result.pin_errors.append(f"pin {pin.number}: " + "; ".join(problems))

    for name, dim in gold.package.dimensions.items():
        other_dim = spec.package.dimensions.get(name)
        if other_dim is None:
            result.dims_missing.append(name)
        elif _same_dim(dim, other_dim):
            result.dims_ok += 1
        else:
            result.dims_wrong.append(name)
    result.dims_extra = sorted(set(spec.package.dimensions) - set(gold.package.dimensions))

    if not result.spec_failures:
        result.symbol_identical = (
            len(spec.pins) == len(gold.pins)
            and result.pins_found == len(gold.pins)
            and result.names_ok == result.types_ok == result.alts_ok == result.groups_ok == len(gold.pins)
        )
        result.footprint_identical = _same_footprint(gold, spec)
    return result


_SUFFIX = re.compile(r"(_run\d+|\.\w+)$")


def case_of(filename: str) -> str:
    """``lm358_soic8_run2.json`` -> ``lm358_soic8``."""
    stem = filename
    while True:
        new = _SUFFIX.sub("", stem)
        if new == stem:
            return stem
        stem = new
