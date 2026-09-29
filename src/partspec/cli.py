"""Command line entry point.

``partspec validate SPEC.json [--datasheet PDF]``
``partspec build SPEC.json --out DIR``
``partspec verify SPEC.json [--symbol FILE] [--footprint FILE]``
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from partspec import api
from partspec.findings import Finding, failed


def _read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"passed": False, "error": f"cannot read {path}: {exc}"}), file=sys.stderr)
    except json.JSONDecodeError as exc:
        print(json.dumps({"passed": False, "error": f"{path} is not valid JSON: {exc}"}), file=sys.stderr)
    return None


def _report(findings: list[Finding], files: list[str] | None = None, *, concise: bool = False) -> int:
    if concise:
        summary = api.summarize(findings, files, api.CONCISE)
        print(json.dumps(summary, indent=2))
        return 0 if summary["passed"] else 1
    report: dict[str, object] = {"passed": not failed(findings)}
    if files is not None:
        report["files"] = files
    report["findings"] = [item.to_dict() for item in findings]
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="partspec")
    sub = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--concise", action="store_true", help="failures in full, warnings only counted by kind")

    validate = sub.add_parser("validate", parents=[common], help="check a PartSpec JSON file")
    validate.add_argument("spec", type=Path)
    validate.add_argument("--datasheet", type=Path, help="also check every quote against this datasheet PDF")

    build = sub.add_parser(
        "build",
        parents=[common],
        help="generate a symbol (and a footprint when the land pattern allows) and verify them",
    )
    build.add_argument("spec", type=Path)
    build.add_argument("--out", type=Path, required=True, help="directory for the generated files")
    build.add_argument("--no-kicad", action="store_true", help="skip loading the result with kicad-cli")
    build.add_argument("--lib-name", default="partspec", help="footprint library nickname (default: partspec)")

    verify = sub.add_parser("verify", parents=[common], help="check existing symbol/footprint files against a PartSpec")
    verify.add_argument("spec", type=Path)
    verify.add_argument("--symbol", type=Path)
    verify.add_argument("--footprint", type=Path)
    verify.add_argument("--no-kicad", action="store_true")

    args = parser.parse_args(argv)
    data = _read_json(args.spec)
    if data is None:
        return 2
    if args.command == "build":
        result = api.build(data, args.out, lib_name=args.lib_name, check_kicad=not args.no_kicad)
        return _report(result.findings, result.files, concise=args.concise)
    if args.command == "verify":
        return _report(
            api.verify_files(data, symbol=args.symbol, footprint=args.footprint, check_kicad=not args.no_kicad),
            concise=args.concise,
        )
    return _report(api.validate(data, args.datasheet), concise=args.concise)


if __name__ == "__main__":
    raise SystemExit(main())
