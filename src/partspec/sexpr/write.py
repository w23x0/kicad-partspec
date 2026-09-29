"""KiCad S-expression writer.

Trees use ``str`` for quoted strings, ``Atom`` for bare tokens, ``int``/``float``
for numbers and ``list`` for nested expressions.  The layout follows KiCad's own
files: tab indentation, short all-scalar lists inline, anything containing a
sub-list broken across lines.
"""

from __future__ import annotations

import math
from typing import Any

from partspec.sexpr.parse import Atom


def format_number(value: int | float) -> str:
    """Format a number the way KiCad does: no exponent, no trailing zeros, no ``-0``."""
    if isinstance(value, bool):
        raise TypeError("bool is not a KiCad value; use Atom('yes') or Atom('no')")
    if isinstance(value, int):
        return str(value)
    if not math.isfinite(value):
        raise ValueError("cannot write a non-finite number")
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _scalar(node: Any) -> str:
    if isinstance(node, Atom):
        return str(node)
    if isinstance(node, str):
        return quote(node)
    if isinstance(node, (int, float)):
        return format_number(node)
    raise TypeError(f"cannot write {type(node).__name__} as an S-expression value")


def _format(node: list[Any], depth: int) -> str:
    if all(not isinstance(item, list) for item in node):
        return "(" + " ".join(_scalar(item) for item in node) + ")"
    lead = 0
    while lead < len(node) and not isinstance(node[lead], list):
        lead += 1
    pad = "\t" * (depth + 1)
    head = " ".join(_scalar(item) for item in node[:lead])
    lines = [f"({head}"]
    for item in node[lead:]:
        lines.append(pad + (_format(item, depth + 1) if isinstance(item, list) else _scalar(item)))
    lines.append("\t" * depth + ")")
    return "\n".join(lines)


def write_sexpr(node: list[Any]) -> str:
    """Serialize one top-level expression, ending with a newline."""
    if not isinstance(node, list):
        raise TypeError("the top level of a KiCad file is a list")
    return _format(node, 0) + "\n"
