"""Symbol generation and the artifact/environment-layer checks.

Planted-error tests edit the *generated* text (parse, change, write) and require
the matching finding, so a check that never fires would fail here.
"""

import copy
import json
import shutil
from pathlib import Path

import pytest

from partspec.cli import main
from partspec.findings import FAIL, failed
from partspec.gen.symbol import build_library, render_library, unit_groups
from partspec.sexpr import Atom, children, first_child, parse_sexpr, write_sexpr
from partspec.spec import load_spec
from partspec.verify.kicad_checks import check_symbol_loads
from partspec.verify.symbol_checks import check_symbol

CASES = Path(__file__).resolve().parent.parent / "evals" / "cases"
NAMES = sorted(p.parent.name for p in CASES.glob("*/spec.gold.json"))
HAS_KICAD = shutil.which("kicad-cli") is not None


def _spec(case):
    spec, findings = load_spec(json.loads((CASES / case / "spec.gold.json").read_text(encoding="utf-8")))
    assert spec is not None, findings
    return spec


def _ids(findings, status=FAIL):
    return {item.id for item in findings if item.status == status}


def _edit(case, mutate):
    """Render the case, apply ``mutate(symbol_node)`` to the parsed tree, return (spec, new text)."""
    spec = _spec(case)
    tree = parse_sexpr(render_library(spec))
    symbol = children(tree[0], "symbol")[0]
    mutate(symbol)
    return spec, write_sexpr(tree[0])


def _xy(pin):
    at = first_child(pin, "at")
    return float(at[1]), float(at[2])


def _units(symbol):
    return children(symbol, "symbol")


def _pin(symbol, number, unit=None):
    for index, sub in enumerate(_units(symbol), start=1):
        for pin in children(sub, "pin"):
            if first_child(pin, "number")[1] == number and unit in (None, index):
                return pin
    raise AssertionError(f"pin {number} not found")


# --------------------------------------------------------------------------- generation


@pytest.mark.parametrize("case", NAMES)
def test_generated_symbol_passes_artifact_checks(case):
    spec = _spec(case)
    assert not failed(check_symbol(spec, render_library(spec)))


@pytest.mark.skipif(not HAS_KICAD, reason="kicad-cli not installed")
@pytest.mark.parametrize("case", NAMES)
def test_generated_symbol_loads_in_kicad(case, tmp_path):
    spec = _spec(case)
    target = tmp_path / "part.kicad_sym"
    target.write_text(render_library(spec), encoding="utf-8")
    assert check_symbol_loads(target, expected_units=len(unit_groups(spec.pins))) == []


def test_generation_is_deterministic_and_reparses_to_the_built_tree():
    spec = _spec("lm358_soic8")
    text = render_library(spec)
    assert text == render_library(spec)
    assert text.endswith(")\n")
    assert parse_sexpr(text)[0] == parse_sexpr(write_sexpr(build_library(spec)))[0]


def test_groups_become_units_with_power_last():
    spec = _spec("lm358_soic8")
    assert unit_groups(spec.pins) == ["A", "B", "power"]
    symbol = children(parse_sexpr(render_library(spec))[0], "symbol")[0]
    assert [unit[1] for unit in _units(symbol)] == ["LM358_1_1", "LM358_2_1", "LM358_3_1"]
    assert {first_child(p, "number")[1] for p in children(_units(symbol)[2], "pin")} == {"4", "8"}


def test_pins_sit_on_the_expected_sides():
    spec = _spec("lm358_soic8")
    symbol = children(parse_sexpr(render_library(spec))[0], "symbol")[0]
    inputs, output = _pin(symbol, "2"), _pin(symbol, "1")
    assert _xy(inputs)[0] < 0 < _xy(output)[0]  # inputs left, output right
    assert _xy(_pin(symbol, "8"))[1] > 0  # supply on top
    assert _xy(_pin(symbol, "4"))[1] < 0  # V- on the bottom


def test_alternate_functions_are_written():
    spec = _spec("atmega328p_tqfp32")
    symbol = children(parse_sexpr(render_library(spec))[0], "symbol")[0]
    alts = {a[1] for a in children(_pin(symbol, "1"), "alternate")}
    assert alts == {"PCINT19", "OC2B", "INT1"}


# --------------------------------------------------------------------------- planted errors


def _remove_pin(number):
    def mutate(symbol):
        for sub in _units(symbol):
            for pin in children(sub, "pin"):
                if first_child(pin, "number")[1] == number:
                    sub.remove(pin)

    return mutate


def _set_number(old, new):
    def mutate(symbol):
        first_child(_pin(symbol, old), "number")[1] = new

    return mutate


def _set_name(number, new):
    def mutate(symbol):
        first_child(_pin(symbol, number), "name")[1] = new

    return mutate


def _set_type(number, new):
    def mutate(symbol):
        _pin(symbol, number)[1] = Atom(new)

    return mutate


def _shift(number, dy):
    def mutate(symbol):
        at = first_child(_pin(symbol, number), "at")
        at[2] = float(at[2]) + dy

    return mutate


def _copy_position(src, dst):
    def mutate(symbol):
        first_child(_pin(symbol, dst), "at")[1:3] = first_child(_pin(symbol, src), "at")[1:3]

    return mutate


def _drop_alternates(number):
    def mutate(symbol):
        pin = _pin(symbol, number)
        for alt in children(pin, "alternate"):
            pin.remove(alt)

    return mutate


def _move_pin_to_unit(number, unit):
    def mutate(symbol):
        pin = _pin(symbol, number)
        for sub in _units(symbol):
            if pin in sub:
                sub.remove(pin)
        _units(symbol)[unit - 1].append(pin)

    return mutate


def _add_pin(number):
    def mutate(symbol):
        clone = copy.deepcopy(_pin(symbol, "1"))
        first_child(clone, "number")[1] = number
        at = first_child(clone, "at")
        at[2] = float(at[2]) + 10 * 1.27  # a free spot
        _units(symbol)[0].append(clone)

    return mutate


PLANTED = [
    ("lm358_soic8", _remove_pin("3"), "symbol.pin_missing"),
    ("lm358_soic8", _add_pin("99"), "symbol.pin_extra"),
    ("lm358_soic8", _set_number("3", "2"), "symbol.pin_duplicate"),
    ("lm358_soic8", _set_number("3", "30"), "symbol.pin_extra"),
    ("lm358_soic8", _set_name("2", "IN1+"), "symbol.pin_mismatch"),
    ("lm358_soic8", _set_type("2", "output"), "symbol.pin_mismatch"),
    ("lm358_soic8", _shift("2", 0.5), "symbol.off_grid"),
    ("lm358_soic8", _copy_position("2", "3"), "symbol.pin_overlap"),
    ("lm358_soic8", _copy_position("2", "3"), "symbol.name_overlap"),
    ("lm358_soic8", _move_pin_to_unit("3", 2), "symbol.unit_mismatch"),
    ("atmega328p_tqfp32", _drop_alternates("1"), "symbol.alt_mismatch"),
    ("tps62130_vqfn16", _shift("10", -7.62), "symbol.name_overlap"),
]


@pytest.mark.parametrize(
    ("case", "mutate", "expected"),
    PLANTED,
    ids=[f"{e}:{m.__qualname__.split('.')[0]}" for _, m, e in PLANTED],
)
def test_planted_error_is_detected(case, mutate, expected):
    spec, text = _edit(case, mutate)
    assert expected in _ids(check_symbol(spec, text))


def test_wrong_symbol_name_and_unparseable_text():
    spec = _spec("lm358_soic8")
    assert "symbol.name_mismatch" in _ids(check_symbol(spec, render_library(spec).replace('"LM358"', '"OTHER"', 1)))
    assert "symbol.unparseable" in _ids(check_symbol(spec, "(kicad_symbol_lib (symbol"))
    assert "symbol.not_a_library" in _ids(check_symbol(spec, "(something)"))


@pytest.mark.skipif(not HAS_KICAD, reason="kicad-cli not installed")
def test_kicad_rejects_an_invalid_pin_type(tmp_path):
    spec = _spec("lm358_soic8")
    target = tmp_path / "bad.kicad_sym"
    target.write_text(render_library(spec).replace("(pin power_in", "(pin power", 1), encoding="utf-8")
    assert "kicad.load_failed" in _ids(check_symbol_loads(target, expected_units=3))


@pytest.mark.skipif(not HAS_KICAD, reason="kicad-cli not installed")
def test_unit_count_mismatch_is_reported(tmp_path):
    spec = _spec("lm358_soic8")
    target = tmp_path / "ok.kicad_sym"
    target.write_text(render_library(spec), encoding="utf-8")
    assert "kicad.unit_count" in _ids(check_symbol_loads(target, expected_units=4))


def test_missing_kicad_cli_is_a_warning_not_a_failure(tmp_path, monkeypatch):
    from partspec.kicad import cli

    monkeypatch.setattr(cli, "CLI_COMMAND", "kicad-cli-definitely-not-installed")
    findings = check_symbol_loads(tmp_path / "x.kicad_sym", expected_units=1)
    assert [item.id for item in findings] == ["kicad.unavailable"] and not failed(findings)


# --------------------------------------------------------------------------- independent oracle

OFFICIAL = Path("/usr/share/kicad/symbols")
ORACLE = {
    "lm358_soic8": ("Amplifier_Operational.kicad_sym", "LM358"),
    "tps62130_vqfn16": ("Regulator_Switching.kicad_sym", "TPS62130"),
    "atmega328p_tqfp32": ("MCU_Microchip_ATmega.kicad_sym", "ATmega328P-A"),
}


def _official_pins(lib, name):
    text = (OFFICIAL / lib).read_text(encoding="utf-8")
    start = text.index(f'(symbol "{name}"')
    depth = 0
    for end in range(start, len(text)):
        depth += {"(": 1, ")": -1}.get(text[end], 0)
        if depth == 0:
            break
    node = parse_sexpr(text[start : end + 1])[0]
    extends = first_child(node, "extends")
    if extends:
        return _official_pins(lib, extends[1])
    found = {}

    def walk(item):
        for child in item[1:]:
            if isinstance(child, list) and child:
                if child[0] == "pin":
                    found[first_child(child, "number")[1]] = (first_child(child, "name")[1], child[1])
                else:
                    walk(child)

    walk(node)
    return found


def _name_compatible(gold_name, official_name):
    """KiCad's libraries use conventions such as +/-/~ for op-amps and merged names like XTAL1/PB6."""
    tokens = [t for t in official_name.replace("~{", "").replace("}", "").split("/") if t]
    return gold_name == "EP" or any(t in {"+", "-", "~"} or gold_name.endswith(t) for t in tokens)


@pytest.mark.skipif(not OFFICIAL.is_dir(), reason="KiCad symbol libraries not installed")
@pytest.mark.parametrize("case", NAMES)
def test_pin_numbers_and_names_agree_with_the_official_kicad_symbol(case):
    lib, name = ORACLE[case]
    official = _official_pins(lib, name)
    spec = _spec(case)
    assert {pin.number for pin in spec.pins} == set(official)
    for pin in spec.pins:
        assert _name_compatible(pin.name, official[pin.number][0]), (pin.number, pin.name, official[pin.number])


@pytest.mark.skipif(not OFFICIAL.is_dir(), reason="KiCad symbol libraries not installed")
def test_lm358_electrical_types_match_the_official_symbol_exactly():
    official = _official_pins(*ORACLE["lm358_soic8"])
    assert {p.number: p.electrical_type for p in _spec("lm358_soic8").pins} == {n: t for n, (_, t) in official.items()}


# --------------------------------------------------------------------------- CLI


def test_cli_build_writes_a_verified_library(tmp_path, capsys):
    spec_path = CASES / "lm358_soic8" / "spec.gold.json"
    assert main(["build", str(spec_path), "--out", str(tmp_path / "out"), "--no-kicad"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["passed"] is True
    written = Path(report["files"][0])
    assert written.name == "LM358.kicad_sym" and written.read_text(encoding="utf-8").startswith("(kicad_symbol_lib")


def test_cli_build_refuses_a_spec_that_fails_validation(tmp_path, capsys):
    data = json.loads((CASES / "lm358_soic8" / "spec.gold.json").read_text(encoding="utf-8"))
    data["pins"].pop()
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    assert main(["build", str(bad), "--out", str(tmp_path / "out"), "--no-kicad"]) == 1
    assert not (tmp_path / "out").exists()
    assert "pins.count_mismatch" in capsys.readouterr().out
