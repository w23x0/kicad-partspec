"""Command line entry point: ``partspec validate SPEC.json``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from partspec.findings import failed
from partspec.verify import verify_spec


def _validate(path: Path) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"passed": False, "error": f"cannot read {path}: {exc}"}), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(json.dumps({"passed": False, "error": f"{path} is not valid JSON: {exc}"}), file=sys.stderr)
        return 2
    findings = verify_spec(data)
    passed = not failed(findings)
    print(json.dumps({"passed": passed, "findings": [item.to_dict() for item in findings]}, indent=2))
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="partspec")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="check a PartSpec JSON file")
    validate.add_argument("spec", type=Path)
    args = parser.parse_args(argv)
    return _validate(args.spec)


if __name__ == "__main__":
    raise SystemExit(main())
