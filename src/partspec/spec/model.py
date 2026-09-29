"""PartSpec data model.

A PartSpec is what the model extracts from a datasheet.  Every extracted value
carries a ``Source`` so a human can audit it against the datasheet page.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Where a value came from.  "extracted": read directly from the datasheet.
# "inferred": derived by the model (needs review).  "confirmed": a human checked it.
STATUSES = ("extracted", "inferred", "confirmed")

# KiCad symbol pin electrical types (the names used in .kicad_sym files).
ELECTRICAL_TYPES = (
    "input",
    "output",
    "bidirectional",
    "tri_state",
    "passive",
    "free",
    "unspecified",
    "power_in",
    "power_out",
    "open_collector",
    "open_emitter",
    "no_connect",
)


@dataclass(frozen=True)
class Source:
    page: int
    quote: str


@dataclass(frozen=True)
class Dimension:
    """A datasheet dimension in millimetres; datasheets give tolerance ranges, not points."""

    min: float | None
    nom: float | None
    max: float | None
    source: Source | None
    status: str = "extracted"


@dataclass(frozen=True)
class Pin:
    number: str
    name: str
    electrical_type: str
    source: Source | None
    status: str = "extracted"
    alt_names: tuple[str, ...] = ()
    group: str | None = None


@dataclass(frozen=True)
class Package:
    family: str
    pin_count: int
    exposed_pad: bool = False
    dimensions: dict[str, Dimension] = field(default_factory=dict)


@dataclass(frozen=True)
class Datasheet:
    sha256: str
    revision: str
    url: str | None = None


@dataclass(frozen=True)
class PartSpec:
    mpn: str
    manufacturer: str
    datasheet: Datasheet
    package: Package
    pins: tuple[Pin, ...]
