"""Spec-layer checker properties, exercised on one synthetic document.

The base document below is SYNTHETIC (an invented 4-pin part) and exists only to
test the checkers; real datasheet-derived cases live in ``evals/cases``. The
planted-error table that used to live here moved to ``tests/test_rules.py``,
where every planted case is named after the rule (SCH-*) it defends, so the
audit in ``scripts/audit.py`` can attribute failures per rule.
"""

import copy
import json

from kicad_partspec.cli import main
from kicad_partspec.verify import verify_spec


def src(page=1, quote="Table 1"):
    return {"page": page, "quote": quote}


BASE = {
    "mpn": "SYNTH-4",
    "manufacturer": "Synthetic",
    "datasheet": {"sha256": "0" * 64, "revision": "A"},
    "package": {
        "family": "SOT",
        "pin_count": 4,
        "exposed_pad": False,
        "dimensions": {"pitch": {"min": 0.9, "nom": 0.95, "max": 1.0, "source": src(2, "e 0.95")}},
    },
    "pins": [
        {"number": "1", "name": "VIN", "electrical_type": "power_in", "source": src()},
        {"number": "2", "name": "GND", "electrical_type": "power_in", "source": src()},
        {"number": "3", "name": "EN", "electrical_type": "input", "source": src()},
        {"number": "4", "name": "VOUT", "electrical_type": "power_out", "source": src()},
    ],
}


def mutated(mutate):
    data = copy.deepcopy(BASE)
    mutate(data)
    return data


def failing_ids(data, status="fail"):
    return {item.id for item in verify_spec(data) if item.status == status}


def test_all_structural_errors_reported_in_one_pass():
    data = mutated(lambda d: (d.pop("mpn"), d["package"].update(pin_count=0), d["pins"][0].pop("name")))
    paths = {item.path for item in verify_spec(data) if item.id == "schema.invalid"}
    assert {".mpn", "package.pin_count", "pins[0].name"} <= paths


def test_findings_carry_actionable_messages():
    for item in verify_spec(mutated(lambda d: d["pins"].pop())):
        assert item.message and item.path


def test_cli_exit_codes(tmp_path, capsys):
    good = tmp_path / "good.json"
    good.write_text(json.dumps(BASE))
    assert main(["validate", str(good)]) == 0
    assert json.loads(capsys.readouterr().out)["passed"] is True

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(mutated(lambda d: d["pins"].pop())))
    assert main(["validate", str(bad)]) == 1
    assert json.loads(capsys.readouterr().out)["passed"] is False

    broken = tmp_path / "broken.json"
    broken.write_text("{not json")
    assert main(["validate", str(broken)]) == 2
    assert main(["validate", str(tmp_path / "missing.json")]) == 2
