"""The scorer is tested on its own: gold against itself, then planted degradations."""

import copy
import json
from pathlib import Path

import pytest

from kicad_partspec.scoring import case_of, score

CASES = Path(__file__).resolve().parent.parent / "evals" / "cases"
NAMES = sorted(p.parent.name for p in CASES.glob("*/spec.gold.json"))


def _gold(case):
    return json.loads((CASES / case / "spec.gold.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", NAMES)
def test_gold_scores_perfectly_against_itself(case):
    gold = _gold(case)
    s = score(case, gold, copy.deepcopy(gold))
    assert s.usable_without_edit
    assert (s.pins_found, s.names_ok, s.types_ok, s.alts_ok, s.groups_ok) == (s.pins_gold,) * 5
    assert s.dims_ok == s.dims_gold and not s.dims_missing and not s.dims_wrong and not s.pin_errors
    assert s.symbol_identical and s.footprint_identical and s.package_ok


def _degrade(case, mutate):
    data = _gold(case)
    mutate(data)
    return score(case, _gold(case), data)


def test_wrong_pin_type_is_counted_and_makes_the_symbol_differ():
    s = _degrade("lm358_soic8", lambda d: d["pins"][0].update(electrical_type="input"))
    assert s.types_ok == s.pins_gold - 1 and not s.symbol_identical and not s.usable_without_edit
    assert "type input != output" in s.pin_errors[0]


def test_wrong_name_missing_pin_and_extra_pin():
    s = _degrade("lm358_soic8", lambda d: d["pins"][1].update(name="INX"))
    assert s.names_ok == s.pins_gold - 1
    s = _degrade("lm358_soic8", lambda d: d["pins"].pop())
    assert s.pins_found == s.pins_gold - 1 and "missing" in s.pin_errors[0]
    s = _degrade("lm358_soic8", lambda d: d["pins"].append({**d["pins"][0], "number": "9"}))
    assert s.pins_extra == 1


def test_dash_variants_and_alt_name_order_do_not_count_as_errors():
    def mutate(d):
        d["pins"][1]["name"] = "IN1–"  # en dash as printed in the datasheet

    assert _degrade("lm358_soic8", mutate).names_ok == 8

    def reorder(d):
        d["pins"][0]["alt_names"] = ["PCINT19", "OC2B", "INT1"][::-1]

    assert _degrade("atmega328p_tqfp32", reorder).alts_ok == 32


def test_group_case_is_ignored_but_a_missing_group_is_not():
    assert _degrade("lm358_soic8", lambda d: d["pins"][0].update(group="a")).groups_ok == 8
    assert _degrade("lm358_soic8", lambda d: d["pins"][0].pop("group")).groups_ok == 7


def test_dimension_errors_are_classified():
    def mutate(d):
        dims = d["package"]["dimensions"]
        dims["pitch"]["nom"] = 1.3
        dims.pop("height")
        dims["extra_dim"] = {"nom": 1.0, "source": {"page": 1, "quote": "x"}}

    s = _degrade("lm358_soic8", mutate)
    assert s.dims_wrong == ["pitch"] and s.dims_missing == ["height"] and s.dims_extra == ["extra_dim"]
    assert s.dims_ok == s.dims_gold - 2


def test_a_wrong_land_pattern_makes_the_footprint_differ_but_not_the_symbol():
    s = _degrade("lm358_soic8", lambda d: d["package"]["dimensions"]["land_span"].update(nom=5.0))
    assert s.symbol_identical and not s.footprint_identical and not s.usable_without_edit


def test_dropping_the_land_pattern_is_a_footprint_disagreement():
    def mutate(d):
        for key in ("land_pad_length", "land_pad_width", "land_span"):
            d["package"]["dimensions"].pop(key)

    assert not _degrade("lm358_soic8", mutate).footprint_identical


def test_two_skipped_footprints_agree():
    gold = _gold("atmega328p_tqfp32")
    assert score("atmega328p_tqfp32", gold, copy.deepcopy(gold)).footprint_identical


def test_a_spec_that_fails_validation_is_never_usable():
    s = _degrade("lm358_soic8", lambda d: d["pins"][0]["source"].update(quote=""))
    assert s.spec_failures == ["prov.missing"] and not s.usable_without_edit


def test_unloadable_extraction_scores_zero_without_crashing():
    s = score("lm358_soic8", _gold("lm358_soic8"), {"mpn": "x"})
    assert not s.loaded and s.pins_found == 0 and not s.usable_without_edit and s.dims_missing
    assert not score("lm358_soic8", _gold("lm358_soic8"), None).loaded


def test_quote_check_counts_bad_quotes_when_pages_are_given():
    pages = ["x"] * 60
    s = score("lm358_soic8", _gold("lm358_soic8"), _gold("lm358_soic8"), pages)
    assert s.quotes_total == 8 + 10 and s.quotes_bad == 18 and not s.usable_without_edit


def test_case_of_strips_run_suffix_and_extension():
    assert case_of("lm358_soic8_run2.json") == "lm358_soic8"
    assert case_of("atmega328p_tqfp32.json") == "atmega328p_tqfp32"


def test_status_disagreement_is_split_into_risky_and_conservative():
    def mutate(d):
        d["pins"][0]["status"] = "inferred"  # gold: extracted -> over-marked, conservative
        d["pins"][3]["status"] = "extracted"  # gold: inferred -> under-marked, risky

    s = _degrade("lm358_soic8", mutate)
    assert (s.status_over, s.status_under, s.status_agree) == (1, 1, 6)
