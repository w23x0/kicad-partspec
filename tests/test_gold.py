import json
import os
import shutil
from pathlib import Path

import pytest

from partspec.findings import failed
from partspec.verify import verify_spec
from partspec.verify.quotes import check_quotes, find_datasheet, normalize, page_texts

CASES = Path(__file__).resolve().parent.parent / "evals" / "cases"
GOLD = sorted(CASES.glob("*/spec.gold.json"))
DATASHEETS = os.environ.get("PARTSPEC_DATASHEETS")


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_gold_cases_exist():
    assert len(GOLD) >= 3


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_gold_passes_spec_layer(path):
    findings = verify_spec(_load(path))
    assert not failed(findings), [item.to_dict() for item in findings if item.status == "fail"]


@pytest.mark.skipif(not DATASHEETS, reason="set PARTSPEC_DATASHEETS to a directory holding the datasheet PDFs")
@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext not installed")
@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_gold_quotes_match_datasheet(path):
    data = _load(path)
    pdf = find_datasheet(data["datasheet"]["sha256"], Path(DATASHEETS))
    assert pdf is not None, "no PDF in PARTSPEC_DATASHEETS matches datasheet.sha256"
    findings = check_quotes(data, page_texts(pdf))
    assert not findings, [item.to_dict() for item in findings]


# --- quote checker, exercised on synthetic page text (no PDF needed) ---------------------------


def _doc(page, quote):
    return {"pins": [{"source": {"page": page, "quote": quote}}], "package": {"dimensions": {}}}


PAGES = ["first page  text", "IN1–   5    2    I   Negative input\nmore"]


def test_quote_found_ignoring_whitespace_and_line_breaks():
    assert check_quotes(_doc(2, "IN1– 5 2 I Negative input more"), PAGES) == []


def test_quote_on_wrong_page_is_reported():
    ids = [f.id for f in check_quotes(_doc(1, "IN1– 5 2 I"), PAGES)]
    assert ids == ["prov.quote_not_found"]


def test_altered_quote_is_reported():
    assert [f.id for f in check_quotes(_doc(2, "IN1– 5 3 I Negative input"), PAGES)] == ["prov.quote_not_found"]


@pytest.mark.parametrize("page", [0, 3, -1])
def test_page_out_of_range_is_reported(page):
    assert [f.id for f in check_quotes(_doc(page, "x"), PAGES)] == ["prov.page_out_of_range"]


def test_dimension_quotes_are_checked_too():
    data = {"pins": [], "package": {"dimensions": {"pitch": {"source": {"page": 1, "quote": "nope"}}}}}
    findings = check_quotes(data, PAGES)
    assert [f.path for f in findings] == ["package.dimensions.pitch.source.quote"]


def test_normalize_collapses_whitespace():
    assert normalize("a \n\t b") == "a b"
