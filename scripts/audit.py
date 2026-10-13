"""The audit: one short, deterministic board for the rules in spec/rules.json.

Usage: python scripts/audit.py [--datasheets DIR]

The board has three layers, all deterministic:

  rule tests   tests/test_rules.py, one node per rule case; the rule-id is in the test name
  gold-spec    verify_spec over every evals/cases/*/spec.gold.json
  gold-quotes  check_quotes against the PDFs in --datasheets (or $PARTSPEC_DATASHEETS)
  gold-build   api.build + kicad-cli load for every gold (the GEN-001 suite)

The previous board is kept in .audit/last.json, so a rule that passed before and
fails now is reported as a regression. The output block is what AGENTS.md calls
the only progress signal; keep it short, fixed-order and parseable.

Exit status: 1 when a rule fails, a rule regressed, or a suite is not fully green.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_FILE = ROOT / "spec" / "rules.json"
CASES = ROOT / "evals" / "cases"
STATE_DIR = ROOT / ".audit"
STATE_FILE = STATE_DIR / "last.json"
RULE_TESTS = ROOT / "tests" / "test_rules.py"

NODE_RE = re.compile(
    r"^tests/test_rules\.py::(?P<node>\S+?)\s+(?P<status>PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b"
)
RULE_ID_RE = re.compile(r"^test_(?P<module>[A-Z]{2,4})_(?P<number>\d{3})_")


def _import_partspec():
    if importlib.util.find_spec("kicad_partspec") is None:
        sys.path.insert(0, str(ROOT / "src"))
    from kicad_partspec import api
    from kicad_partspec.findings import failed
    from kicad_partspec.verify import verify_spec
    from kicad_partspec.verify.quotes import check_quotes, find_datasheet, page_texts

    return api, failed, verify_spec, check_quotes, find_datasheet, page_texts


def _rules() -> list[dict]:
    return json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]


def _rule_tests() -> dict[str, str]:
    """Run the rule tests once and map rule-id -> status, plus any node without a rule-id."""
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, [str(ROOT), os.environ.get("PYTHONPATH")])))
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(RULE_TESTS.relative_to(ROOT)),
            "-o",
            "addopts=",
            "-v",
            "--tb=no",
            "--color=no",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    statuses: dict[str, str] = {}
    unruled: list[str] = []
    for line in result.stdout.splitlines():
        match = NODE_RE.match(line)
        if not match:
            continue
        node, status = match.group("node"), match.group("status")
        rule = RULE_ID_RE.match(node)
        if rule is None:
            unruled.append(node)
            continue
        rule_id = f"{rule.group('module')}-{rule.group('number')}"
        previous = statuses.get(rule_id, "PASSED")
        # One failing case fails the rule; a skipped case does not pass it.
        statuses[rule_id] = "FAILED" if "FAILED" in (status, previous) else status
    if result.returncode not in (0, 1):
        for line in result.stdout.splitlines()[-20:]:
            print(f"  pytest: {line}")
    return statuses, unruled, result.stdout


def _gold_documents() -> list[tuple[str, dict]]:
    return [
        (path.parent.name, json.loads(path.read_text(encoding="utf-8"))) for path in sorted(CASES.glob("*/spec.gold.json"))
    ]


def _suite_gold_spec(verify_spec, failed) -> tuple[int, int, list[str]]:
    documents = _gold_documents()
    bad = [case for case, data in documents if failed(verify_spec(data))]
    return len(documents) - len(bad), len(documents), bad


def _suite_gold_quotes(check_quotes, find_datasheet, page_texts, datasheets: Path | None) -> tuple[str, list[str]]:
    if datasheets is None or shutil.which("pdftotext") is None:
        return "skipped", []
    bad = []
    total = 0
    for case, data in _gold_documents():
        pdf = find_datasheet(data["datasheet"]["sha256"], datasheets)
        if pdf is None:
            bad.append(f"{case}: no matching PDF")
            continue
        total += 1
        if check_quotes(data, page_texts(pdf)):
            bad.append(case)
    return f"{total - len(bad)}/{total}", bad


def _suite_gold_build(api, failed) -> tuple[str, list[str]]:
    """Build and load every gold; the footprint is skipped (with a reason) when the land pattern is incomplete."""
    documents = _gold_documents()
    bad: list[str] = []
    mods = 0
    skipped = 0
    with tempfile.TemporaryDirectory(prefix="partspec-audit-") as tmp:
        for case, data in documents:
            result = api.build(data, Path(tmp) / case, lib_name="audit", check_kicad=True)
            if failed(result.findings):
                bad.append(case)
            mods += sum(1 for name in result.files if name.endswith(".kicad_mod"))
            skipped += sum(1 for item in result.findings if item.id == "footprint.skipped")
    return f"{len(documents) - len(bad)}/{len(documents)} ({mods} mods, {skipped} skipped)", bad


def _previous() -> dict:
    if not STATE_FILE.is_file():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _board(rules, statuses, suite_results, previous):
    """The counts behind the printed board, as a dict.

    A rule whose only test was SKIPPED is neither failing nor uncovered, but it did not run:
    it must not be counted as passing (AGENTS.md allows skipif only for a missing
    environment, and the three gold suites already degrade to warnings, not successes, when
    tools are absent). `previous` is the state file's contents, for 退步.
    """
    covered = [rule["id"] for rule in rules if rule["id"] in statuses or rule.get("suite")]
    failing = [rule["id"] for rule in rules if statuses.get(rule["id"]) == "FAILED"]
    skipped = [rule["id"] for rule in rules if statuses.get(rule["id"]) == "SKIPPED"]
    uncovered = [rule["id"] for rule in rules if rule["id"] not in covered]
    passing = [
        rule["id"]
        for rule in rules
        if rule["id"] in covered and rule["id"] not in failing and rule["id"] not in skipped
    ]

    regressed = [
        rule["id"]
        for rule in rules
        if previous.get("rules", {}).get(rule["id"]) == "pass" and statuses.get(rule["id"]) == "FAILED"
    ]
    for name, (ok, _, _) in suite_results.items():
        if previous.get("suites", {}).get(name) is True and not ok:
            regressed.append(name)

    return {
        "covered": covered,
        "passing": passing,
        "failing": failing,
        "skipped": skipped,
        "uncovered": uncovered,
        "regressed": sorted(set(regressed)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasheets", type=Path, default=os.environ.get("PARTSPEC_DATASHEETS"))
    args = parser.parse_args()

    rules = _rules()
    statuses, unruled, _ = _rule_tests()

    api, failed, verify_spec, check_quotes, find_datasheet, page_texts = _import_partspec()
    spec_ok, spec_total, spec_bad = _suite_gold_spec(verify_spec, failed)
    quote_line, quote_bad = _suite_gold_quotes(check_quotes, find_datasheet, page_texts, args.datasheets)
    build_line, build_bad = _suite_gold_build(api, failed)

    previous = _previous()
    suite_results = {
        "gold-spec": (spec_bad == [], spec_ok, spec_total),
        # A skipped quote layer (no datasheet directory) reports itself and does not decide the board.
        "gold-quotes": (quote_bad == [], quote_line, None),
        "gold-build": (build_bad == [], build_line, None),
    }

    board = _board(rules, statuses, suite_results, previous)
    covered = board["covered"]
    failing = board["failing"]
    skipped = board["skipped"]
    uncovered = board["uncovered"]
    passing = board["passing"]
    regressed = board["regressed"]

    print(f"规则总数: {len(rules)}")
    print(f"有测试:   {len(covered)}")
    print(f"通过:     {len(passing)}")
    print(f"未通过:   {failing}")
    print(f"退步:     {sorted(set(regressed))}")
    if skipped:
        print(f"跳过:     {skipped}")
    print(f"未覆盖:   {uncovered}")
    if unruled:
        print(f"无规则号: {unruled}")
    print(f"gold-spec:   {spec_ok}/{spec_total}")
    print(f"gold-quotes: {quote_line}")
    print(f"gold-build:  {build_line}")
    for case in spec_bad + quote_bad + build_bad:
        print(f"  failing: {case}")

    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(
            {
                "rules": {rule["id"]: ("pass" if rule["id"] in passing else "fail") for rule in rules},
                "suites": {name: ok for name, (ok, _, _) in suite_results.items()},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    green = not failing and not regressed and all(ok for ok, _, _ in suite_results.values())
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
