"""Score extracted PartSpecs against the gold cases.

Usage: python evals/score.py --extracted DIR --datasheets DIR [--out results.json]

DIR/<case>.json or DIR/<case>_runN.json is scored against evals/cases/<case>/spec.gold.json.
The datasheet PDFs (matched by SHA-256) let the quote check run; without them quotes are not scored.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from partspec.scoring import Score, case_of, score
from partspec.verify.quotes import find_datasheet, page_texts

CASES = Path(__file__).parent / "cases"


def _pct(part: int, whole: int) -> str:
    return f"{part}/{whole}" if whole else "-"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extracted", type=Path, required=True)
    parser.add_argument("--datasheets", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    scores: list[tuple[str, Score]] = []
    page_cache: dict[str, list[str]] = {}
    for path in sorted(args.extracted.glob("*.json")):
        case = case_of(path.name)
        gold_path = CASES / case / "spec.gold.json"
        if not gold_path.is_file():
            print(f"skipping {path.name}: no gold case named {case!r}", file=sys.stderr)
            continue
        gold = json.loads(gold_path.read_text(encoding="utf-8"))
        try:
            extracted = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"{path.name}: not valid JSON ({exc})", file=sys.stderr)
            extracted = None
        pages = None
        if args.datasheets is not None:
            sha = gold["datasheet"]["sha256"]
            if sha not in page_cache:
                pdf = find_datasheet(sha, args.datasheets)
                if pdf is not None:
                    page_cache[sha] = page_texts(pdf)
            pages = page_cache.get(sha)
        scores.append((path.stem, score(case, gold, extracted, pages)))

    print("| run | pins | names | types | alts | groups | dims | quotes bad | symbol | footprint | usable as-is |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for name, s in scores:
        quotes = "-" if s.quotes_total is None else _pct(s.quotes_bad or 0, s.quotes_total)
        print(
            f"| {name} | {_pct(s.pins_found, s.pins_gold)} | {_pct(s.names_ok, s.pins_gold)} | {_pct(s.types_ok, s.pins_gold)} "
            f"| {_pct(s.alts_ok, s.pins_gold)} | {_pct(s.groups_ok, s.pins_gold)} | {_pct(s.dims_ok, s.dims_gold)} | {quotes} "
            f"| {'same' if s.symbol_identical else 'differs'} | {'same' if s.footprint_identical else 'differs'} "
            f"| {'YES' if s.usable_without_edit else 'no'} |"
        )
    usable = sum(1 for _, s in scores if s.usable_without_edit)
    print(f"\nusable without edit: {usable}/{len(scores)}")
    if args.out:
        args.out.write_text(
            json.dumps({name: s.to_dict() for name, s in scores}, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
