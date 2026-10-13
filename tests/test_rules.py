"""Conformance tests named after the rule-ids in ``spec/rules.json``.

Every test function here is named ``test_<RULE-ID>_<slug>`` so that
``scripts/audit.py`` can attribute a failure to one rule. Two test kinds carry
a rule-id:

* fixture tests, which plant one error in a synthetic document (or in synthetic
  page text) and assert the checker reports it -- these defend SCH-* and SRC-*;
* corpus tests, which assert the gold cases in ``evals/cases`` obey an
  extraction rule -- these defend MPN/PIN/STAT/DIM/LAND, whose subject is the
  model reading a datasheet, so there is no code path to exercise.

Wording guards for the same prose live in ``tests/test_skill_*.py`` on purpose:
they pin the instruction text, not a behaviour, and are not audit-visible.

A rule with no test here shows up in the audit board as uncovered (DIM-004 today). That is deliberate: writing a fake test for it would hide the gap the board exists to show.
"""

import json
import re
from pathlib import Path

import pytest

from kicad_partspec.findings import WARN, failed
from kicad_partspec.verify import verify_spec
from kicad_partspec.verify.quotes import check_quotes
from test_skill_dimension_rules import NAMES
from test_spec_checks import BASE, failing_ids, mutated, src

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evals" / "cases"
GOLD = sorted(CASES.glob("*/spec.gold.json"))

SUPPLY_TYPES = {"power_in", "power_out"}
EXPOSED_PAD_GOLDS = ["drv8871_soic8", "tps62130_vqfn16", "cp2102n_qfn24", "tps5430_soic8"]


def gold(case):
    return json.loads((CASES / case / "spec.gold.json").read_text(encoding="utf-8"))


def pins_of(case):
    return gold(case)["pins"]


def pin(case, number):
    return next(p for p in pins_of(case) if p["number"] == number)


def dim(case, name):
    return gold(case)["package"]["dimensions"][name]


# A range as the drawing prints it: `4.81-5.00`, `0.31 - 0.51`, `.005-.010`. Note numbers glued to a
# letter (`D(1)`) and degrees (`0 -8`) are excluded by the decimal endpoints.
RANGE_QUOTE = re.compile(r"(?<![0-9.])(?:\d+\.\d+|\.\d+)\s*[-\u2013]\s*(?:\d+\.\d+|\.\d+)(?![0-9.])")
BRACKET_QUOTE = re.compile(r"\[\s*(?:\d+\.\d+|\.\d+)\s*[-\u2013]\s*(?:\d+\.\d+|\.\d+)\s*\]")


# --- SCH-001..006: the spec-layer checkers, one planted error per case ---------------------------------


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["pins"][0].pop("source"),
        lambda d: d["pins"][1]["source"].update(quote=" "),
        lambda d: d["pins"][2]["source"].update(page=0),
        lambda d: d["package"]["dimensions"]["pitch"].pop("source"),
    ],
    ids=["pin without source", "empty quote", "page zero", "dimension without source"],
)
def test_SCH_001_every_value_cites_a_page_and_quote(mutate):
    assert "prov.missing" in failing_ids(mutated(mutate))


def test_SCH_001_a_complete_document_passes():
    assert not failed(verify_spec(BASE))


@pytest.mark.parametrize(
    "mutate",
    [lambda d: d["pins"].pop(), lambda d: d["pins"].append({**d["pins"][0], "number": "5"})],
    ids=["pin dropped", "pin added"],
)
def test_SCH_002_pin_count_matches_the_pins_array(mutate):
    assert "pins.count_mismatch" in failing_ids(mutated(mutate))


def test_SCH_002_the_exposed_pad_adds_one_expected_pin():
    data = mutated(lambda d: d["package"].update(exposed_pad=True))
    assert "pins.count_mismatch" in failing_ids(data)
    data["pins"].append({"number": "EP", "name": "GND", "electrical_type": "power_in", "source": src()})
    assert not failed(verify_spec(data))


def test_SCH_003_pin_numbers_are_unique():
    data = mutated(lambda d: d["pins"][1].update(number="1"))
    assert "pins.duplicate_number" in failing_ids(data)


def test_SCH_004_electrical_type_is_a_kicad_type():
    data = mutated(lambda d: d["pins"][0].update(electrical_type="power"))
    assert "pins.bad_type" in failing_ids(data)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["package"]["dimensions"]["pitch"].update(min=1.2),
        lambda d: d["package"]["dimensions"]["pitch"].update(min=-0.1),
        lambda d: d["package"]["dimensions"]["pitch"].update(min=0.0, nom=0.0, max=0.0),
        lambda d: d["package"]["dimensions"].update(pitch={"source": src()}),
    ],
    ids=["min above max", "negative value", "zero maximum", "no value at all"],
)
def test_SCH_005_dimension_values_are_ordered_and_positive(mutate):
    assert failing_ids(mutated(mutate)) & {"dim.order", "dim.non_positive", "dim.empty"}


def test_SCH_005_a_zero_minimum_is_allowed():
    data = mutated(lambda d: d["package"]["dimensions"]["pitch"].update(min=0.0, nom=0.5, max=1.0))
    assert not failed(verify_spec(data))


def test_SCH_006_a_bad_status_is_a_failure():
    data = mutated(lambda d: d["pins"][0].update(status="guessed"))
    assert "status.invalid" in failing_ids(data)


def test_SCH_006_an_inferred_value_is_a_warning_not_a_failure():
    data = mutated(lambda d: d["pins"][0].update(status="inferred"))
    findings = verify_spec(data)
    assert not failed(findings)
    assert "status.inferred" in {item.id for item in findings if item.status == WARN}


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_SCH_007_pin_numbers_are_strings(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data["pins"]:
        assert isinstance(item["number"], str), f"{path.parent.name}: pin {item['number']!r} is not a string"


# --- SRC-001..005: the quote checker, exercised on synthetic page text (no PDF needed) ------------------

PAGES = ["first page  text", "IN1–   5    2    I   Negative input\nmore"]


def _doc(page, quote):
    return {"pins": [{"source": {"page": page, "quote": quote}}], "package": {"dimensions": {}}}


def test_SRC_001_a_quote_matches_ignoring_whitespace_and_line_breaks():
    assert check_quotes(_doc(2, "IN1– 5 2 I Negative input more"), PAGES) == []


def test_SRC_002_a_quote_on_another_page_is_reported():
    ids = [item.id for item in check_quotes(_doc(1, "IN1– 5 2 I"), PAGES)]
    assert ids == ["prov.quote_not_found"]


def test_SRC_003_an_altered_quote_is_reported():
    findings = check_quotes(_doc(2, "IN1– 5 3 I Negative input"), PAGES)
    assert [item.id for item in findings] == ["prov.quote_not_found"]


@pytest.mark.parametrize("page", [0, 3, -1])
def test_SRC_004_a_page_outside_the_pdf_is_reported(page):
    findings = check_quotes(_doc(page, "x"), PAGES)
    assert [item.id for item in findings] == ["prov.page_out_of_range"]


def test_SRC_005_dimension_sources_are_checked_too():
    data = {"pins": [], "package": {"dimensions": {"pitch": {"source": {"page": 1, "quote": "nope"}}}}}
    findings = check_quotes(data, PAGES)
    assert [item.path for item in findings] == ["package.dimensions.pitch.source.quote"]


# --- MPN-001: the orderable as the datasheet prints it -------------------------------------------------


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_MPN_001_the_mpn_is_one_printed_token(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    mpn = data["mpn"]
    assert mpn and mpn == mpn.strip() and len(mpn.split()) == 1, f"{path.parent.name}: mpn {mpn!r}"


@pytest.mark.parametrize(
    ("case", "expected"),
    [("ads1015_vssop10", "ADS1015IDGSR"), ("tps5430_soic8", "TPS5430DDA"), ("tca9548a_tssop24", "TCA9548APWR")],
)
def test_MPN_001_the_orderable_keeps_its_suffix(case, expected):
    """The three golds whose orderable is not the bare device name: package and reel suffixes stay on."""
    assert gold(case)["mpn"] == expected


# --- PIN-001/002: names and alternate names ------------------------------------------------------------


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_PIN_001_alt_names_are_functions_not_descriptions(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data["pins"]:
        for alt in item.get("alt_names") or []:
            assert alt and "/" not in alt and not alt.endswith("."), f"{path.parent.name}: pin {item['number']}"


@pytest.mark.parametrize("case", EXPOSED_PAD_GOLDS)
def test_PIN_001_an_exposed_pad_carries_no_alt_names(case):
    """The pad row exists in these four golds; the other EP gold (rp2040) folds its pad into a GND row."""
    pads = [p for p in pins_of(case) if p["name"] in ("EP", "PAD", "DAP")]
    assert len(pads) == 1, f"{case}: expected one exposed-pad row"
    assert not pads[0].get("alt_names"), f"{case}: the exposed pad has alt names"
    assert pads[0]["electrical_type"] == "power_in", f"{case}: the exposed pad is not a supply"


def test_PIN_002_a_sibling_parts_name_is_an_alt_name_of_nothing():
    """MCP23008's table pairs its pins with the MCP23017's (SCL/SCK, A2/SO, NC/CS); none is our alt name."""
    paired = {"SCL", "SDA", "A0", "A1", "A2", "RESET-", "NC"}
    for item in pins_of("mcp23008_soic18"):
        if item["name"] in paired:
            assert not item.get("alt_names"), f"pin {item['name']} took a sibling part's name as an alt name"


# --- PIN-003: grouping repeated functional blocks ------------------------------------------------------


def test_PIN_003_both_pins_of_a_channel_share_one_key():
    """ULN2003A: each channel's base (nB) and collector (nC) share the channel number as the group key."""
    channels = {item["name"][0] for item in pins_of("uln2003a_tssop16") if item["name"][1:2] in ("B", "C")}
    assert channels == {str(n) for n in range(1, 8)}
    for item in pins_of("uln2003a_tssop16"):
        if item["name"][1:2] in ("B", "C"):
            assert item["group"] == item["name"][0], item["name"]


def test_PIN_003_the_key_is_the_datasheets_own_label():
    for item in pins_of("tca9548a_tssop24"):
        if item["name"].startswith(("SD", "SC")) and item["name"][2:].isdigit():
            assert item["group"] == f"CH{item['name'][2:]}", item["name"]
    for item in pins_of("lm358_soic8"):
        if item["name"] in ("OUT1", "IN1-", "IN1+"):
            assert item["group"] == "A"
        if item["name"] in ("IN2+", "IN2-", "OUT2"):
            assert item["group"] == "B"


def test_PIN_003_single_instance_pins_stay_ungrouped():
    """MCP23008's GP0-GP7 are one port, not repeated blocks; its address, reset and select pins have no unit."""
    assert all(item.get("group") is None for item in pins_of("mcp23008_soic18"))
    for item in pins_of("tca9548a_tssop24"):
        if item["name"] in ("A0", "A1", "A2", "RESET"):
            assert item.get("group") is None, item["name"]


# --- PIN-004: the supply group and its carve-outs ------------------------------------------------------


def test_PIN_004_a_node_shared_by_every_unit_is_not_a_supply():
    """ULN2003A's COM (pin 9) is touched by all seven flyback diodes, yet the sheet says the part needs no supply."""
    com, emitter = pin("uln2003a_tssop16", "9"), pin("uln2003a_tssop16", "8")
    assert com["name"] == "COM"
    assert com["electrical_type"] == "passive"
    assert com.get("group") is None
    assert emitter["name"] == "E"
    assert emitter["electrical_type"] == "power_in"
    assert emitter["group"] == "power"


def test_PIN_004_a_printed_supply_block_is_grouped_power():
    """DRV8871 prints GND/VM/PGND/PAD in a TYPE column of their own; every one is grouped power."""
    for number in ("1", "5", "7", "9"):
        item = pin("drv8871_soic8", number)
        assert item["electrical_type"] == "power_in", number
        assert item["group"] == "power", number


def test_PIN_004_lone_supplies_may_stay_ungrouped():
    """NE555 prints no supply block; VCC and GND are the part's only supplies and stay ungrouped."""
    for number in ("1", "8"):
        item = pin("ne555_soic8", number)
        assert item["electrical_type"] == "power_in", number
        assert item.get("group") is None, number


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_PIN_004_a_power_group_holds_supplies_and_nothing_else(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data["pins"]:
        if item.get("group") == "power":
            assert item.get("electrical_type") in SUPPLY_TYPES, f"{path.parent.name}: pin {item['number']}"


# --- PIN-005: the electrical_type mapping --------------------------------------------------------------


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_PIN_005_supplies_are_typed_as_power(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data["pins"]:
        if item["name"] in ("VCC", "VDD", "VSS", "GND", "V+", "V-", "VM", "PGND", "VIO", "VBAT", "USB"):
            assert item["electrical_type"] in SUPPLY_TYPES, f"{path.parent.name}: pin {item['number']} {item['name']}"


def test_PIN_005_an_open_drain_output_is_open_collector():
    assert pin("ne555_soic8", "7")["name"] == "DISCH"
    assert pin("ne555_soic8", "7")["electrical_type"] == "open_collector"
    assert pin("ads1015_vssop10", "2")["name"] == "ALERT/RDY"
    assert pin("ads1015_vssop10", "2")["electrical_type"] == "open_collector"
    for item in pins_of("uln2003a_tssop16"):
        if item["name"].endswith("C"):
            assert item["electrical_type"] == "open_collector", item["name"]


def test_PIN_005_three_state_outputs_are_tri_state():
    """74HC595: Q0-Q7 go high-impedance while OE is HIGH; the daisy-chain Q7S never does."""
    chip = {item["name"]: item for item in pins_of("74hc595_so16")}
    for name in (f"Q{n}" for n in range(8)):
        assert chip[name]["electrical_type"] == "tri_state", name
    assert chip["Q7S"]["electrical_type"] == "output"
    assert chip["OE"]["electrical_type"] == "input"


def test_PIN_005_an_exposed_pad_is_a_supply():
    assert pin("tps5430_soic8", "9")["electrical_type"] == "power_in"
    assert pin("tps62130_vqfn16", "17")["electrical_type"] == "power_in"


# --- STAT-001/002: the status vocabulary ---------------------------------------------------------------


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_STAT_001_derived_types_are_marked_inferred(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data["pins"]:
        if item["electrical_type"] in (*SUPPLY_TYPES, "open_collector"):
            assert item["status"] == "inferred", f"{path.parent.name}: pin {item['number']} {item['name']}"


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_STAT_002_confirmed_is_reserved_for_humans(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert all(item.get("status") != "confirmed" for item in data["pins"])
    assert all(value.get("status") != "confirmed" for value in data["package"]["dimensions"].values())


# --- DIM-002/003/005 and LAND-001: dimension naming ----------------------------------------------------


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_DIM_002_every_dimension_name_is_defined(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    unknown = set(data["package"]["dimensions"]) - NAMES
    assert not unknown, f"{path.parent.name}: undefined dimension names {sorted(unknown)}"


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_DIM_001_a_printed_range_becomes_min_and_max(path):
    """DIM-001: a range the sheet prints (`4.81-5.00`, `0.31 - 0.51`, `.005-.010`) is `min` plus
    `max` -- both endpoints, never one of them, and never a `nom` added on top. When the quote
    carries both units (`.005-.010 TYP [0.13-0.25]`) the spec records the metric pair.

    The other forms DIM-001 lists (a lone `MAX`, a `TYP`/`BSC` value, `X ± t`) cannot be read off a
    `pdftotext` quote: the quotes mix several callouts of one drawing on a line, so no quote-level
    test can attribute a marker to the dimension it belongs to. They have no checker and no other
    test here.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    for name, value in data["package"]["dimensions"].items():
        quote = value["source"]["quote"]
        if not RANGE_QUOTE.search(quote):
            continue
        assert value.get("nom") is None, f"{path.parent.name}: {name} has a nom {value['nom']} on a range {quote!r}"
        assert value.get("min") is not None and value.get("max") is not None, (
            f"{path.parent.name}: {name} records only part of range {quote!r}"
        )
        assert value["min"] < value["max"], f"{path.parent.name}: {name} min>=max on {quote!r}"
        metric = BRACKET_QUOTE.search(quote)
        if metric:
            low, high = (float(x) for x in metric.group(0).strip("[]").replace(" ", "").split("-"))
            assert (value["min"], value["max"]) == (low, high), (
                f"{path.parent.name}: {name} ignores the printed {metric.group(0)}"
            )


def test_DIM_003_ne555_standoff_spans_body_underside_to_seating_plane():
    """The round-4 adjudication: the [0.11-0.25] extension lines run to the dashed seating line, so it is a standoff."""
    value = dim("ne555_soic8", "standoff")
    assert (value["min"], value["max"]) == (0.11, 0.25)


def test_DIM_003_drv8871_lead_callouts_are_named_by_their_spans():
    """DETAIL A's arrows: standoff underside-to-seating-plane, lead_length tip to where the bend starts."""
    assert (dim("drv8871_soic8", "standoff")["min"], dim("drv8871_soic8", "standoff")["max"]) == (0.0, 0.15)
    assert (dim("drv8871_soic8", "lead_length")["min"], dim("drv8871_soic8", "lead_length")["max"]) == (0.4, 1.27)


@pytest.mark.parametrize("case", ["stm32g030_tssop20", "74hc595_so16"])
def test_DIM_005_letter_tables_become_canonical_names(case):
    """ST and Nexperia print letters; the golds carry the canonical names A->height, A1->standoff, Lp->lead_length."""
    names = set(gold(case)["package"]["dimensions"])
    for name in ("height", "standoff", "lead_length"):
        assert name in names, f"{case}: {name} missing"
    assert not any(len(name) <= 2 and name.isalpha() and name not in NAMES for name in names)


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_LAND_001_the_land_set_is_recorded_whole_or_not_at_all(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    names = data["package"]["dimensions"]
    present = [name for name in ("land_pad_length", "land_pad_width", "land_span") if name in names]
    assert present in ([], ["land_pad_length", "land_pad_width", "land_span"]), f"{path.parent.name}: {present}"


def test_LAND_001_land_dimensions_are_the_metal_not_the_mask_opening():
    """DRV8871's land pattern prints a mask rectangle smaller than the metal; the gold records the metal (2.95)."""
    assert dim("drv8871_soic8", "land_ep_size")["nom"] == 2.95
