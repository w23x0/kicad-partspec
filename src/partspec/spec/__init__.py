"""PartSpec model and loader."""

from partspec.spec.load import load_spec
from partspec.spec.model import ELECTRICAL_TYPES, STATUSES, PartSpec

__all__ = ["ELECTRICAL_TYPES", "STATUSES", "PartSpec", "load_spec"]
