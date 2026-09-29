"""Spec-layer checks, exercised by planting one error at a time.

The base document below is SYNTHETIC (an invented 4-pin part) and exists only to
test the checkers; real datasheet-derived cases live in ``evals/cases``.
"""

import copy
import json

import pytest

from partspec.cli import main
from partspec.findings import FAIL, WARN, failed
from partspec.verify import verify_spec


def _src(page=1, quote="Table 1"):
    return {"page": page, "quote": quote}


BASE = {
    "mpn": "SYNTH-4",
    "manufacturer": "Synthetic",
    "datasheet": {"sha256": "0" * 64, "revision": "A"},
    "package": {
        "family": "SOT",
        "pin_count": 4,
        "exposed_pad": False,
        "dimensions": {"pitch": {"min": 0.9, "nom": 0.95, "max": 1.0, "source": _src(2, "e 0.95")}},
    },
    "pins": [
        {"number": "1", "name": "VIN", "electrical_type": "power_in", "source": _src()},
        {"number": "2", "name": "GND", "electrical_type": "power_in", "source": _src()},
        {"number": "3", "name": "EN", "electrical_type": "input", "source": _src()},
        {"number": "4", "name": "VOUT", "electrical_type": "power_out", "source": _src()},
    ],
}


def _mutated(mutate):
    data = copy.deepcopy(BASE)
    mutate(data)
    return data


def _ids(data, status=FAIL):
    return {item.id for item in verify_spec(data) if item.status == status}


def test_valid_base_has_no_failures():
    assert not failed(verify_spec(BASE))


# (name, mutation, expected finding id)
PLANTED = [
    ("missing source", lambda d: d["pins"][0].pop("source"), "prov.missing"),
    ("empty quote", lambda d: d["pins"][1]["source"].update(quote=" "), "prov.missing"),
    ("page zero", lambda d: d["pins"][2]["source"].update(page=0), "prov.missing"),
    ("dimension without source", lambda d: d["package"]["dimensions"]["pitch"].pop("source"), "prov.missing"),
    ("pin dropped", lambda d: d["pins"].pop(), "pins.count_mismatch"),
    ("pin added", lambda d: d["pins"].append({**d["pins"][0], "number": "5"}), "pins.count_mismatch"),
    ("duplicate number", lambda d: d["pins"][1].update(number="1"), "pins.duplicate_number"),
    ("bad type", lambda d: d["pins"][0].update(electrical_type="power"), "pins.bad_type"),
    ("min above max", lambda d: d["package"]["dimensions"]["pitch"].update(min=1.2), "dim.order"),
    ("negative dimension", lambda d: d["package"]["dimensions"]["pitch"].update(min=-0.1), "dim.non_positive"),
    (
        "zero maximum",
        lambda d: d["package"]["dimensions"]["pitch"].update(min=0.0, nom=0.0, max=0.0),
        "dim.non_positive",
    ),
    ("empty dimension", lambda d: d["package"]["dimensions"].update(pitch={"source": _src()}), "dim.empty"),
    ("bad status", lambda d: d["pins"][0].update(status="guessed"), "status.invalid"),
    ("pin_count not int", lambda d: d["package"].update(pin_count="4"), "schema.invalid"),
    ("pins not a list", lambda d: d.update(pins="none"), "schema.invalid"),
    ("mpn missing", lambda d: d.pop("mpn"), "schema.invalid"),
    ("page not int", lambda d: d["pins"][0]["source"].update(page="3"), "schema.invalid"),
]


@pytest.mark.parametrize(("mutate", "expected"), [(m, e) for _, m, e in PLANTED], ids=[n for n, _, _ in PLANTED])
def test_planted_error_is_detected(mutate, expected):
    assert expected in _ids(_mutated(mutate))


def test_zero_minimum_is_allowed():
    data = _mutated(lambda d: d["package"]["dimensions"]["pitch"].update(min=0.0, nom=0.5, max=1.0))
    assert not failed(verify_spec(data))


def test_exposed_pad_adds_one_expected_pin():
    data = _mutated(lambda d: d["package"].update(exposed_pad=True))
    assert "pins.count_mismatch" in _ids(data)
    data["pins"].append({"number": "EP", "name": "GND", "electrical_type": "power_in", "source": _src()})
    assert not failed(verify_spec(data))


def test_inferred_value_is_a_warning_not_a_failure():
    data = _mutated(lambda d: d["pins"][0].update(status="inferred"))
    findings = verify_spec(data)
    assert not failed(findings)
    assert "status.inferred" in {item.id for item in findings if item.status == WARN}


def test_all_structural_errors_reported_in_one_pass():
    data = _mutated(lambda d: (d.pop("mpn"), d["package"].update(pin_count=0), d["pins"][0].pop("name")))
    paths = {item.path for item in verify_spec(data) if item.id == "schema.invalid"}
    assert {".mpn", "package.pin_count", "pins[0].name"} <= paths


def test_findings_carry_actionable_messages():
    for item in verify_spec(_mutated(lambda d: d["pins"].pop())):
        assert item.message and item.path


def test_cli_exit_codes(tmp_path, capsys):
    good = tmp_path / "good.json"
    good.write_text(json.dumps(BASE))
    assert main(["validate", str(good)]) == 0
    assert json.loads(capsys.readouterr().out)["passed"] is True

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(_mutated(lambda d: d["pins"].pop())))
    assert main(["validate", str(bad)]) == 1
    assert json.loads(capsys.readouterr().out)["passed"] is False

    broken = tmp_path / "broken.json"
    broken.write_text("{not json")
    assert main(["validate", str(broken)]) == 2
    assert main(["validate", str(tmp_path / "missing.json")]) == 2
