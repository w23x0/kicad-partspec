"""Check every gold case: spec-layer checks plus quotes against the datasheet PDFs.

Usage: python evals/check_gold.py [--datasheets DIR]

The PDFs are not stored in this repository.  Put them in DIR (or set
PARTSPEC_DATASHEETS); each is matched to its case by the SHA-256 in the spec.
Without a datasheet directory only the spec-layer checks run.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from kicad_partspec.findings import FAIL, Finding, failed
from kicad_partspec.verify import verify_spec
from kicad_partspec.verify.quotes import check_quotes, find_datasheet, page_texts

CASES = Path(__file__).parent / "cases"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasheets", type=Path, default=os.environ.get("PARTSPEC_DATASHEETS"))
    args = parser.parse_args()
    datasheets = Path(args.datasheets) if args.datasheets else None

    exit_code = 0
    for spec_path in sorted(CASES.glob("*/spec.gold.json")):
        case = spec_path.parent.name
        data = json.loads(spec_path.read_text(encoding="utf-8"))
        findings = verify_spec(data)
        note = ""
        if datasheets is None:
            note = " (quotes not checked: no datasheet directory)"
        else:
            pdf = find_datasheet(data["datasheet"]["sha256"], datasheets)
            if pdf is None:
                findings.append(
                    Finding(
                        "prov.datasheet_missing",
                        FAIL,
                        f"no PDF in {datasheets} matches datasheet.sha256; download the exact revision named in the spec.",
                        path="datasheet.sha256",
                    )
                )
            else:
                findings.extend(check_quotes(data, page_texts(pdf)))
        bad = [item for item in findings if item.status == FAIL]
        warnings = [item for item in findings if item.status != FAIL]
        print(f"{case}: {'FAIL' if failed(findings) else 'ok'} ({len(bad)} failures, {len(warnings)} warnings){note}")
        for item in bad:
            print(f"  {item.id} {item.path}: {item.message}")
        if failed(findings):
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
