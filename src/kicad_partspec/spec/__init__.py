"""PartSpec model and loader."""

from kicad_partspec.spec.load import load_spec
from kicad_partspec.spec.model import ELECTRICAL_TYPES, STATUSES, PartSpec

__all__ = ["ELECTRICAL_TYPES", "STATUSES", "PartSpec", "load_spec"]
