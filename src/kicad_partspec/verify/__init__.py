"""Verification entry points."""

from __future__ import annotations

from typing import Any

from kicad_partspec.findings import Finding
from kicad_partspec.spec import load_spec
from kicad_partspec.verify.spec_checks import SPEC_CHECKS


def verify_spec(data: Any) -> list[Finding]:
    """Structural load, then every spec-layer check.  Returns all findings."""
    spec, findings = load_spec(data)
    if spec is None:
        return findings
    for check in SPEC_CHECKS:
        findings.extend(check(spec))
    return findings


__all__ = ["verify_spec"]
