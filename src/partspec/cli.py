"""Command line entry point: ``partspec validate SPEC.json`` and ``partspec build SPEC.json --out DIR``."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from partspec.findings import Finding, failed
from partspec.gen.symbol import render_library, unit_groups
from partspec.spec import load_spec
from partspec.verify import verify_spec
from partspec.verify.kicad_checks import check_symbol_loads
from partspec.verify.symbol_checks import check_symbol


def _read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"passed": False, "error": f"cannot read {path}: {exc}"}), file=sys.stderr)
    except json.JSONDecodeError as exc:
        print(json.dumps({"passed": False, "error": f"{path} is not valid JSON: {exc}"}), file=sys.stderr)
    return None


def _report(findings: list[Finding], files: list[str] | None = None) -> int:
    passed = not failed(findings)
    report: dict[str, object] = {"passed": passed}
    if files is not None:
        report["files"] = files
    report["findings"] = [item.to_dict() for item in findings]
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


def _validate(path: Path) -> int:
    data = _read_json(path)
    if data is None:
        return 2
    return _report(verify_spec(data))


def _file_stem(mpn: str) -> str:
    return re.sub(r"[^A-Za-z0-9._+-]", "_", mpn)


def _build(path: Path, out: Path, *, check_kicad: bool) -> int:
    data = _read_json(path)
    if data is None:
        return 2
    findings = verify_spec(data)
    if failed(findings):
        return _report(findings)  # never generate from a spec that fails its own checks
    spec, _ = load_spec(data)
    assert spec is not None
    text = render_library(spec)
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{_file_stem(spec.mpn)}.kicad_sym"
    target.write_text(text, encoding="utf-8")
    findings.extend(check_symbol(spec, text))
    if check_kicad:
        findings.extend(check_symbol_loads(target, expected_units=len(unit_groups(spec.pins))))
    return _report(findings, files=[str(target)])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="partspec")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="check a PartSpec JSON file")
    validate.add_argument("spec", type=Path)
    build = sub.add_parser("build", help="generate a KiCad symbol library from a PartSpec and verify it")
    build.add_argument("spec", type=Path)
    build.add_argument("--out", type=Path, required=True, help="directory for the generated files")
    build.add_argument("--no-kicad", action="store_true", help="skip loading the result with kicad-cli")
    args = parser.parse_args(argv)
    if args.command == "build":
        return _build(args.spec, args.out, check_kicad=not args.no_kicad)
    return _validate(args.spec)


if __name__ == "__main__":
    raise SystemExit(main())
