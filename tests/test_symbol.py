"""Symbol generation and the artifact/environment-layer checks.

Planted-error tests edit the *generated* text (parse, change, write) and require
the matching finding, so a check that never fires would fail here.
"""

import copy
import json
import shutil
from pathlib import Path

import pytest

from kicad_partspec.cli import main
from kicad_partspec.findings import FAIL, failed
from kicad_partspec.gen.symbol import build_library, render_library, unit_groups
from kicad_partspec.sexpr import Atom, children, first_child, parse_sexpr, write_sexpr
from kicad_partspec.spec import load_spec
from kicad_partspec.verify.kicad_checks import check_symbol_loads
from kicad_partspec.verify.symbol_checks import check_symbol

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
    from kicad_partspec.kicad import cli

    monkeypatch.setattr(cli, "CLI_COMMAND", "kicad-cli-definitely-not-installed")
    findings = check_symbol_loads(tmp_path / "x.kicad_sym", expected_units=1)
    assert [item.id for item in findings] == ["kicad.unavailable"] and not failed(findings)


# --------------------------------------------------------------------------- independent oracle

OFFICIAL = Path("/usr/share/kicad/symbols")
ORACLE = {
    "lm358_soic8": ("Amplifier_Operational.kicad_sym", "LM358"),
    "tps62130_vqfn16": ("Regulator_Switching.kicad_sym", "TPS62130"),
    "atmega328p_tqfp32": ("MCU_Microchip_ATmega.kicad_sym", "ATmega328P-A"),
    "ina219_soic8": ("Sensor_Energy.kicad_sym", "INA219AxD"),
    "txs0108e_tssop20": ("Logic_LevelTranslator.kicad_sym", "TXS0108EPW"),
    "ads1115_vssop10": ("Analog_ADC.kicad_sym", "ADS1115IDGS"),
    "tps54202_sot23": ("Regulator_Switching.kicad_sym", "TPS54202DDC"),
    "rp2040_qfn56": ("MCU_RaspberryPi.kicad_sym", "RP2040"),
    "74hc595_so16": ("74xx.kicad_sym", "74HC595"),
    "stm32g030_tssop20": ("MCU_ST_STM32G0.kicad_sym", "STM32G030F6Px"),
    "cp2102n_qfn24": ("Interface_USB.kicad_sym", "CP2102N-Axx-xQFN24"),
    "ads1015_vssop10": ("Analog_ADC.kicad_sym", "ADS1015IDGS"),
    "drv8871_soic8": ("Driver_Motor.kicad_sym", "DRV8871DDA"),
    "mcp23008_soic18": ("Interface_Expansion.kicad_sym", "MCP23008-xSO"),
    "sn74lvc2t45_vssop8": ("Logic_LevelTranslator.kicad_sym", "SN74LVC2T45DCUR"),
    "tlc555_soic8": ("Timer.kicad_sym", "TLC555xD"),
    "tca9548a_tssop24": ("Interface_Expansion.kicad_sym", "TCA9548APWR"),
    "ne555_soic8": ("Timer.kicad_sym", "NE555D"),
    "tps5430_soic8": ("Regulator_Switching.kicad_sym", "TPS5430DDA"),
    "uln2003a_tssop16": ("Transistor_Array.kicad_sym", "ULN2003A"),
    "24lc256_soic8": ("Memory_EEPROM.kicad_sym", "24LC256"),
    "ina226_vssop10": ("Sensor_Energy.kicad_sym", "INA226"),
    "pca9306_vssop8": ("Interface.kicad_sym", "PCA9306"),
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
    """KiCad's libraries use conventions such as +/-/~ for op-amps, merged names like XTAL1/PB6 and an overbar where
    datasheets write an active-low suffix (RSTb, QSPI_SS_N); ST datasheets print PC15-OSC32_OUT and VDD/VDDA where
    KiCad has PC15 and VDD."""
    tokens = [t for t in official_name.replace("~{", "").replace("}", "").split("/") if t]
    active_low = gold_name.removesuffix("_N").removesuffix("b") if official_name.startswith("~{") else gold_name
    first = gold_name.replace("/", "-").split("-")[0]
    return gold_name == "EP" or any(
        t in {"+", "-", "~"} or gold_name.endswith(t) or active_low == t or first == t for t in tokens
    )


# Parts whose datasheet and KiCad name pins by different vendors' conventions; see the case's review.md.
RENAMED = {
    "24lc256_soic8": {  # Microchip calls the ground pin VSS and never writes GND; KiCad normalises supply rails to GND
        "4": "GND",
    },
    "74hc595_so16": {  # Nexperia Q0-Q7/DS/SHCP/STCP/MR against TI's QA-QH/SER/SRCLK/RCLK/SRCLR
        "1": "QB",
        "2": "QC",
        "3": "QD",
        "4": "QE",
        "5": "QF",
        "6": "QG",
        "7": "QH",
        "9": "QH'",
        "10": "~{SRCLR}",
        "11": "SRCLK",
        "12": "RCLK",
        "14": "SER",
        "15": "QA",
    },
    "drv8871_soic8": {  # TI prints PGND (7) and PAD (9); the library calls both GND
        "7": "GND",
        "9": "GND",
    },
    "tlc555_soic8": {  # TI prints RESET (4) and VDD (8) against the NE555 family's ~{RST} and VCC
        "4": "~{RST}",
        "8": "VCC",
    },
    "ina226_vssop10": {  # TI prints VBUS and IN-/IN+ on the pin table; KiCad writes Vbus and uses the shunt-terminal form Vin-/Vin+
        "8": "Vbus",
        "9": "Vin-",
        "10": "Vin+",
    },
    "ne555_soic8": {  # TI prints RESET on pin 4; KiCad writes the active-low abbreviation
        "4": "~{RST}",
    },
    "tps5430_soic8": {  # TI prints ENA and DAP; KiCad abbreviates to EN and calls the thermal pad GNDPAD
        "5": "EN",
        "9": "GNDPAD",
    },
    "uln2003a_tssop16": {  # TI labels channels 1B-7B/1C-7C and the common emitter E; KiCad uses I1-I7/O1-O7 and GND
        "1": "I1",
        "2": "I2",
        "3": "I3",
        "4": "I4",
        "5": "I5",
        "6": "I6",
        "7": "I7",
        "8": "GND",
        "10": "O7",
        "11": "O6",
        "12": "O5",
        "13": "O4",
        "14": "O3",
        "15": "O2",
        "16": "O1",
    },
}


@pytest.mark.skipif(not OFFICIAL.is_dir(), reason="KiCad symbol libraries not installed")
@pytest.mark.parametrize("case", NAMES)
def test_pin_numbers_and_names_agree_with_the_official_kicad_symbol(case):
    if case not in ORACLE:
        pytest.skip(f"no official KiCad symbol recorded for {case}")
    lib, name = ORACLE[case]
    official = _official_pins(lib, name)
    spec = _spec(case)
    assert {pin.number for pin in spec.pins} == set(official)
    renamed = RENAMED.get(case, {})
    for pin in spec.pins:
        if pin.number in renamed:
            assert official[pin.number][0] == renamed[pin.number], (pin.number, official[pin.number])
            continue
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


def test_cli_concise_output_names_the_failures_and_counts_the_warnings(tmp_path, capsys):
    spec_path = CASES / "atmega328p_tqfp32" / "spec.gold.json"
    assert main(["build", str(spec_path), "--out", str(tmp_path), "--no-kicad", "--concise"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["passed"] is True and report["failed"] == [] and "findings" not in report
    assert report["warning_summary"]["footprint.skipped"] == 1  # not buried among the per-pin warnings
    assert report["warning_summary"]["status.inferred"] > 1
