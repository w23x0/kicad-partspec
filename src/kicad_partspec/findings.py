"""Machine-readable verification results shared by every check."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

PASS = "pass"
WARN = "warn"
FAIL = "fail"


@dataclass(frozen=True)
class Finding:
    """One check outcome.

    ``message`` must say how to fix the problem, because an agent reads it to
    decide its next edit.  ``path`` points into the PartSpec JSON document.
    """

    id: str
    status: str
    message: str
    path: str = ""
    expected: Any = None
    actual: Any = None
    refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value not in (None, "", [])}


def failed(findings: list[Finding]) -> bool:
    return any(item.status == FAIL for item in findings)
