"""Structural loading of a PartSpec from a JSON document.

Problems are reported as findings with JSON paths instead of raised, so an
agent gets every structural error in one pass.
"""

from __future__ import annotations

from typing import Any

from partspec.findings import FAIL, Finding
from partspec.spec.model import Datasheet, Dimension, Package, PartSpec, Pin, Source

_SCHEMA = "schema.invalid"


class _Collector:
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def error(self, path: str, message: str, expected: Any = None, actual: Any = None) -> None:
        self.findings.append(Finding(_SCHEMA, FAIL, message, path=path, expected=expected, actual=actual))

    def obj(self, value: Any, path: str) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        self.error(path, f"{path or 'document'} must be a JSON object", "object", type(value).__name__)
        return {}

    def string(self, parent: dict[str, Any], key: str, path: str, *, required: bool = True) -> str:
        value = parent.get(key)
        if isinstance(value, str) and value.strip():
            return value
        if value is not None or required:
            self.error(f"{path}.{key}", f"{path}.{key} must be a non-empty string", "non-empty string", value)
        return ""

    def number(self, parent: dict[str, Any], key: str, path: str) -> float | None:
        value = parent.get(key)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            self.error(f"{path}.{key}", f"{path}.{key} must be a number or null", "number", value)
            return None
        return float(value)


def _source(c: _Collector, parent: dict[str, Any], path: str) -> Source | None:
    raw = parent.get("source")
    if raw is None:
        return None  # missing provenance is a semantic finding, not a structural one
    src = c.obj(raw, f"{path}.source")
    page = src.get("page")
    if isinstance(page, bool) or not isinstance(page, int):
        c.error(f"{path}.source.page", "source.page must be an integer", "integer", page)
        page = 0
    quote = src.get("quote", "")
    if not isinstance(quote, str):
        c.error(f"{path}.source.quote", "source.quote must be a string", "string", quote)
        quote = ""
    # An empty or blank quote is loadable; the provenance check reports it.
    return Source(page=page, quote=quote)


def _status(c: _Collector, parent: dict[str, Any], path: str) -> str:
    value = parent.get("status", "extracted")
    if isinstance(value, str):
        return value
    c.error(f"{path}.status", f"{path}.status must be a string", "string", value)
    return "extracted"


def _dimension(c: _Collector, raw: Any, path: str) -> Dimension:
    dim = c.obj(raw, path)
    return Dimension(
        min=c.number(dim, "min", path),
        nom=c.number(dim, "nom", path),
        max=c.number(dim, "max", path),
        source=_source(c, dim, path),
        status=_status(c, dim, path),
    )


def _pin(c: _Collector, raw: Any, path: str) -> Pin:
    pin = c.obj(raw, path)
    number = pin.get("number")
    if isinstance(number, int) and not isinstance(number, bool):
        number = str(number)
    if not isinstance(number, str) or not number.strip():
        c.error(f"{path}.number", f"{path}.number must be a non-empty string or integer", "string", number)
        number = ""
    alt = pin.get("alt_names", [])
    if not isinstance(alt, list) or not all(isinstance(item, str) for item in alt):
        c.error(f"{path}.alt_names", f"{path}.alt_names must be a list of strings", "list[str]", alt)
        alt = []
    group = pin.get("group")
    if group is not None and not isinstance(group, str):
        c.error(f"{path}.group", f"{path}.group must be a string or null", "string", group)
        group = None
    return Pin(
        number=number,
        name=c.string(pin, "name", path),
        electrical_type=c.string(pin, "electrical_type", path),
        source=_source(c, pin, path),
        status=_status(c, pin, path),
        alt_names=tuple(alt),
        group=group,
    )


def _package(c: _Collector, raw: Any) -> Package:
    pkg = c.obj(raw, "package")
    count = pkg.get("pin_count")
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        c.error("package.pin_count", "package.pin_count must be a positive integer", "positive integer", count)
        count = 0
    exposed = pkg.get("exposed_pad", False)
    if not isinstance(exposed, bool):
        c.error("package.exposed_pad", "package.exposed_pad must be a boolean", "boolean", exposed)
        exposed = False
    raw_dims = pkg.get("dimensions", {})
    dims: dict[str, Dimension] = {}
    for name, value in c.obj(raw_dims, "package.dimensions").items():
        dims[str(name)] = _dimension(c, value, f"package.dimensions.{name}")
    return Package(family=c.string(pkg, "family", "package"), pin_count=count, exposed_pad=exposed, dimensions=dims)


def load_spec(data: Any) -> tuple[PartSpec | None, list[Finding]]:
    """Return the parsed spec, or ``None`` plus every structural finding."""
    c = _Collector()
    root = c.obj(data, "")
    ds = c.obj(root.get("datasheet"), "datasheet")
    raw_pins = root.get("pins")
    pins: list[Pin] = []
    if not isinstance(raw_pins, list) or not raw_pins:
        c.error("pins", "pins must be a non-empty list", "non-empty list", raw_pins)
    else:
        pins = [_pin(c, item, f"pins[{index}]") for index, item in enumerate(raw_pins)]
    spec = PartSpec(
        mpn=c.string(root, "mpn", ""),
        manufacturer=c.string(root, "manufacturer", ""),
        datasheet=Datasheet(
            sha256=c.string(ds, "sha256", "datasheet"),
            revision=c.string(ds, "revision", "datasheet"),
            url=c.string(ds, "url", "datasheet", required=False) or None,
        ),
        package=_package(c, root.get("package")),
        pins=tuple(pins),
    )
    return (None, c.findings) if c.findings else (spec, [])
