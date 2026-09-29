"""Source-layer check: every quoted string must appear on its cited datasheet page.

This re-reads the datasheet instead of trusting the spec.  It shells out to
``pdftotext -layout`` (poppler) and compares whitespace-collapsed text.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

from partspec.findings import FAIL, Finding

_WHITESPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip()


def page_texts(pdf: Path, *, timeout: int = 120) -> list[str]:
    """Return the layout text of each page, index 0 being page 1."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("pdftotext was not found on PATH (install poppler-utils)") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"pdftotext timed out after {timeout} seconds") from exc
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext failed on {pdf}: {result.stderr.strip()}")
    pages = result.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()  # pdftotext ends the last page with a form feed
    return pages


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_datasheet(sha256: str, directory: Path) -> Path | None:
    """Locate the PDF in ``directory`` whose SHA-256 matches the spec's pin."""
    for candidate in sorted(directory.glob("*.pdf")):
        if sha256_of(candidate) == sha256:
            return candidate
    return None


def _sources(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    found: list[tuple[str, dict[str, Any]]] = []
    for index, pin in enumerate(data.get("pins") or []):
        if isinstance(pin, dict) and isinstance(pin.get("source"), dict):
            found.append((f"pins[{index}].source", pin["source"]))
    dims = (data.get("package") or {}).get("dimensions") or {}
    for name, dim in dims.items():
        if isinstance(dim, dict) and isinstance(dim.get("source"), dict):
            found.append((f"package.dimensions.{name}.source", dim["source"]))
    return found


_MAX_HINT_GAP = 8  # other tokens allowed between the quoted ones when suggesting a fix


def suggest_quote(quote: str, page: str) -> str | None:
    """The shortest stretch of the page that holds the quote's tokens in order, or None.

    Layout text often puts other labels between numbers that belong together
    (``1.0 C 0.8``); quoting that stretch verbatim passes the check.
    """
    wanted = normalize(quote).split(" ")
    tokens = normalize(page).split(" ")
    best: list[str] | None = None
    limit = len(wanted) + _MAX_HINT_GAP
    for start, token in enumerate(tokens):
        if token != wanted[0]:
            continue
        position, matched = start, 1
        while matched < len(wanted) and position + 1 < min(len(tokens), start + limit):
            position += 1
            if tokens[position] == wanted[matched]:
                matched += 1
        if matched == len(wanted) and (best is None or position - start + 1 < len(best)):
            best = tokens[start : position + 1]
    if best is None or best == wanted:
        return None
    return " ".join(best)


def check_quotes(data: dict[str, Any], pages: list[str]) -> list[Finding]:
    """Compare every source quote with the text of its cited page."""
    normalized: dict[int, str] = {}
    findings: list[Finding] = []
    for path, source in _sources(data):
        page, quote = source.get("page"), source.get("quote")
        if not isinstance(page, int) or not isinstance(quote, str) or not quote.strip():
            continue  # structural / provenance checks already report these
        if not 1 <= page <= len(pages):
            findings.append(
                Finding(
                    "prov.page_out_of_range",
                    FAIL,
                    f"{path}.page {page} is outside the datasheet (1..{len(pages)}); cite the page the quote is on.",
                    path=f"{path}.page",
                    expected=f"1..{len(pages)}",
                    actual=page,
                )
            )
            continue
        text = normalized.setdefault(page, normalize(pages[page - 1]))
        if normalize(quote) not in text:
            hint = suggest_quote(quote, text)
            advice = (
                f" The page prints these tokens as {hint!r}; quote exactly that."
                if hint
                else " Copy the text exactly as printed by `pdftotext -layout`, or check the page number."
            )
            findings.append(
                Finding(
                    "prov.quote_not_found",
                    FAIL,
                    f"{path}.quote does not appear on datasheet page {page}." + advice,
                    path=f"{path}.quote",
                    expected=hint,
                    actual=quote,
                )
            )
    return findings
