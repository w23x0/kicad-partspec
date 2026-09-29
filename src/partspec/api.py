"""Operations shared by the CLI and the MCP server.

Everything here returns findings instead of raising on bad input, so callers
(and agents) always get the full list of problems in one pass.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from partspec.findings import FAIL, WARN, Finding, failed
from partspec.gen.footprint import footprint_name, render_footprint, skip_reason
from partspec.gen.symbol import render_library, unit_groups
from partspec.spec import load_spec
from partspec.verify import verify_spec
from partspec.verify.footprint_checks import check_footprint
from partspec.verify.kicad_checks import check_footprint_loads, check_symbol_loads
from partspec.verify.quotes import check_quotes, page_texts, sha256_of
from partspec.verify.symbol_checks import check_symbol

CONCISE = "concise"
DETAILED = "detailed"


@dataclass
class Result:
    findings: list[Finding]
    files: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not failed(self.findings)


def file_stem(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._+-]", "_", name)


def validate(data: Any, datasheet: Path | None = None) -> list[Finding]:
    """Spec-layer checks, plus the source check when the datasheet PDF is given."""
    findings = verify_spec(data)
    if datasheet is None or not isinstance(data, dict):
        return findings
    if not datasheet.is_file():
        return [
            *findings,
            Finding("prov.datasheet_unreadable", FAIL, f"the datasheet file {datasheet} does not exist."),
        ]
    declared = (data.get("datasheet") or {}).get("sha256") if isinstance(data.get("datasheet"), dict) else None
    actual = sha256_of(datasheet)
    if declared != actual:
        findings.append(
            Finding(
                "prov.datasheet_sha_mismatch",
                FAIL,
                f"datasheet.sha256 is {declared!r} but the PDF's SHA-256 is {actual}; set datasheet.sha256 to that value.",
                path="datasheet.sha256",
                expected=actual,
                actual=declared,
            )
        )
    try:
        findings.extend(check_quotes(data, page_texts(datasheet)))
    except RuntimeError as exc:
        findings.append(Finding("prov.datasheet_unreadable", FAIL, f"could not read the datasheet text: {exc}."))
    return findings


def build(data: Any, out: Path, *, lib_name: str = "partspec", check_kicad: bool = True) -> Result:
    """Generate and verify the symbol and, when the land pattern allows, the footprint."""
    findings = verify_spec(data)
    if failed(findings):
        return Result(findings)  # never generate from a spec that fails its own checks
    spec, _ = load_spec(data)
    assert spec is not None
    out.mkdir(parents=True, exist_ok=True)
    files: list[str] = []

    footprint_ref: str | None = None
    reason = skip_reason(spec)
    if reason is None:
        name = footprint_name(spec)
        text = render_footprint(spec, name)
        pretty = out / f"{lib_name}.pretty"
        pretty.mkdir(exist_ok=True)
        target = pretty / f"{file_stem(name)}.kicad_mod"
        target.write_text(text, encoding="utf-8")
        files.append(str(target))
        footprint_ref = f"{lib_name}:{name}"
        findings.extend(check_footprint(spec, text))
        if check_kicad:
            findings.extend(check_footprint_loads(pretty, name=file_stem(name)))
    else:
        findings.append(Finding("footprint.skipped", WARN, f"no footprint was generated: {reason}."))

    symbol_text = render_library(spec, footprint_ref)
    symbol_file = out / f"{file_stem(spec.mpn)}.kicad_sym"
    symbol_file.write_text(symbol_text, encoding="utf-8")
    files.insert(0, str(symbol_file))
    findings.extend(check_symbol(spec, symbol_text, expected_footprint=footprint_ref or ""))
    if check_kicad:
        findings.extend(check_symbol_loads(symbol_file, expected_units=len(unit_groups(spec.pins))))
    return Result(findings, files)


def verify_files(
    data: Any,
    *,
    symbol: Path | None = None,
    footprint: Path | None = None,
    check_kicad: bool = True,
) -> list[Finding]:
    """Check existing symbol and/or footprint files against a spec (they may come from anywhere)."""
    findings = verify_spec(data)
    if failed(findings):
        return findings
    spec, _ = load_spec(data)
    assert spec is not None
    if symbol is None and footprint is None:
        return [*findings, Finding("verify.nothing", FAIL, "pass a symbol file, a footprint file, or both.")]
    if symbol is not None:
        try:
            text = symbol.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(Finding("verify.unreadable", FAIL, f"cannot read {symbol}: {exc}."))
        else:
            findings.extend(check_symbol(spec, text))
            if check_kicad:
                findings.extend(check_symbol_loads(symbol, expected_units=len(unit_groups(spec.pins))))
    if footprint is not None:
        try:
            text = footprint.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(Finding("verify.unreadable", FAIL, f"cannot read {footprint}: {exc}."))
        else:
            findings.extend(check_footprint(spec, text))
            if check_kicad:
                with tempfile.TemporaryDirectory(prefix="partspec-pretty-") as temporary:
                    pretty = Path(temporary) / "check.pretty"
                    pretty.mkdir()
                    shutil.copy(footprint, pretty / footprint.name)
                    findings.extend(check_footprint_loads(pretty, name=footprint.stem))
    return findings


def summarize(
    result_findings: list[Finding], files: list[str] | None = None, response_format: str = CONCISE
) -> dict[str, Any]:
    """A result an agent can act on: failures first; detail only on request."""
    failures = [item for item in result_findings if item.status == FAIL]
    warnings = [item for item in result_findings if item.status == WARN]
    report: dict[str, Any] = {
        "passed": not failures,
        "failures": len(failures),
        "warnings": len(warnings),
    }
    if files is not None:
        report["files"] = files
    if response_format == DETAILED:
        report["findings"] = [item.to_dict() for item in result_findings]
    else:
        report["failed"] = [{"id": item.id, "path": item.path, "message": item.message} for item in failures]
        if warnings:
            counts: dict[str, int] = {}
            for item in warnings:
                counts[item.id] = counts.get(item.id, 0) + 1
            report["warning_summary"] = counts
    return report
