"""Footprint generation and its artifact/environment-layer checks.

Planted-error tests edit the *generated* text (parse, change, write) and require
the matching finding, so a check that never fires would fail here.
"""

import copy
import json
import shutil
from pathlib import Path

import pytest

from partspec.cli import main
from partspec.findings import FAIL, WARN, failed
from partspec.gen.footprint import (
    _clip,
    _silk_segments,
    compute_pads,
    footprint_name,
    render_footprint,
    skip_reason,
)
from partspec.gen.symbol import render_library
from partspec.sexpr import Atom, children, first_child, parse_sexpr, write_sexpr
from partspec.spec import load_spec
from partspec.verify.footprint_checks import check_footprint
from partspec.verify.kicad_checks import check_footprint_loads
from partspec.verify.symbol_checks import check_symbol

CASES = Path(__file__).resolve().parent.parent / "evals" / "cases"
SUPPORTED = ["lm358_soic8", "tps62130_vqfn16"]
HAS_KICAD = shutil.which("kicad-cli") is not None


def _data(case):
    return json.loads((CASES / case / "spec.gold.json").read_text(encoding="utf-8"))


def _spec(case, mutate=None):
    data = _data(case)
    if mutate:
        mutate(data)
    spec, findings = load_spec(data)
    assert spec is not None, findings
    return spec


def _ids(findings, status=FAIL):
    return {item.id for item in findings if item.status == status}


def _edit(case, mutate):
    spec = _spec(case)
    tree = parse_sexpr(render_footprint(spec))
    mutate(tree[0])
    return spec, write_sexpr(tree[0])


def _pad(fp, number):
    for pad in children(fp, "pad"):
        if pad[1] == number:
            return pad
    raise AssertionError(number)


def _xy(pad):
    at = first_child(pad, "at")
    return float(at[1]), float(at[2])


# --------------------------------------------------------------------------- generation


@pytest.mark.parametrize("case", SUPPORTED)
def test_generated_footprint_passes_artifact_checks(case):
    spec = _spec(case)
    assert skip_reason(spec) is None
    assert check_footprint(spec, render_footprint(spec)) == []


@pytest.mark.skipif(not HAS_KICAD, reason="kicad-cli not installed")
@pytest.mark.parametrize("case", SUPPORTED)
def test_generated_footprint_loads_in_kicad(case, tmp_path):
    spec = _spec(case)
    name = footprint_name(spec)
    pretty = tmp_path / "lib.pretty"
    pretty.mkdir()
    (pretty / f"{name}.kicad_mod").write_text(render_footprint(spec), encoding="utf-8")
    assert check_footprint_loads(pretty, name=name) == []


def test_generation_is_deterministic():
    spec = _spec("lm358_soic8")
    assert render_footprint(spec) == render_footprint(spec)


def test_names_follow_the_kicad_convention():
    assert footprint_name(_spec("lm358_soic8")) == "SOIC-8_3.9x4.9mm_P1.27mm"
    assert footprint_name(_spec("tps62130_vqfn16")) == "QFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm"


def test_soic_pads_are_numbered_counter_clockwise_from_the_top_left():
    pads = {pad.number: pad for pad in compute_pads(_spec("lm358_soic8"))}
    assert (pads["1"].x < 0, pads["1"].y < 0) == (True, True)
    assert (pads["4"].x < 0, pads["4"].y > 0) == (True, True)
    assert (pads["5"].x > 0, pads["5"].y > 0) == (True, True)
    assert (pads["8"].x > 0, pads["8"].y < 0) == (True, True)
    assert (pads["1"].width, pads["1"].height) == (1.55, 0.6)  # the datasheet land pattern
    assert abs(pads["1"].x) == pytest.approx(2.7)  # land_span 5.4 / 2


def test_quad_pads_run_counter_clockwise_and_the_exposed_pad_is_last():
    pads = {pad.number: pad for pad in compute_pads(_spec("tps62130_vqfn16"))}
    assert pads["1"].x < 0 and pads["1"].y < 0  # top of the left column
    assert pads["5"].y > 0 and pads["5"].x < 0  # left end of the bottom row
    assert pads["9"].x > 0 and pads["9"].y > 0  # bottom of the right column
    assert pads["13"].y < 0 and pads["13"].x > 0  # right end of the top row
    assert (pads["17"].x, pads["17"].y, pads["17"].width, pads["17"].shape) == (0, 0, 1.68, "rect")
    assert (pads["5"].width, pads["5"].height) == (0.24, 0.6)  # top/bottom pads are turned


def test_symbol_footprint_field_points_at_the_generated_footprint():
    spec = _spec("lm358_soic8")
    ref = f"lib:{footprint_name(spec)}"
    assert not failed(check_symbol(spec, render_library(spec, ref), expected_footprint=ref))
    assert "symbol.footprint_mismatch" in _ids(check_symbol(spec, render_library(spec), expected_footprint=ref))


# --------------------------------------------------------------------------- skipping


def test_atmega_is_skipped_because_the_datasheet_gives_no_land_pattern():
    reason = skip_reason(_spec("atmega328p_tqfp32"))
    assert reason and "land_pad_length" in reason and "land_span" in reason


def test_unsupported_family_odd_pin_count_and_missing_ep_size_are_skipped():
    assert "not supported" in skip_reason(_spec("lm358_soic8", lambda d: d["package"].update(family="BGA")))
    assert "even" in skip_reason(_spec("lm358_soic8", lambda d: d["package"].update(pin_count=7)))
    assert "divisible by 4" in skip_reason(_spec("tps62130_vqfn16", lambda d: d["package"].update(pin_count=15)))
    assert "land_ep_size" in skip_reason(
        _spec("tps62130_vqfn16", lambda d: d["package"]["dimensions"].pop("land_ep_size"))
    )
    assert "non-square" in skip_reason(
        _spec("tps62130_vqfn16", lambda d: d["package"]["dimensions"]["body_width"].update(min=3.9, max=4.1))
    )


# --------------------------------------------------------------------------- silkscreen clipping


class _Pad:
    def __init__(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height


def test_clip_removes_only_the_part_near_a_pad():
    pad = _Pad(0, 1, 2, 1)  # spans x -1..1, y 0.5..1.5; with margin 0.5 the keep-out is x -1.5..1.5, y 0..2
    assert _clip((-3, 1, 3, 1), [pad], 0.5) == [(-3, 1, -1.5, 1), (1.5, 1, 3, 1)]
    assert _clip((-3, 3, 3, 3), [pad], 0.5) == [(-3, 3, 3, 3)]  # far away: untouched
    assert _clip((-1.2, 1, 1.2, 1), [pad], 0.5) == []  # fully inside the keep-out
    assert _clip((0, -3, 0, 5), [pad], 0.5) == [(0, -3, 0, 0), (0, 2, 0, 5)]  # vertical segment through the pad


def test_silkscreen_stays_clear_of_every_pad():
    for case in SUPPORTED:
        spec = _spec(case)
        pads = compute_pads(spec)
        assert _silk_segments(spec, pads)  # something is drawn


# --------------------------------------------------------------------------- planted errors


def _remove_pad(number):
    return lambda fp: fp.remove(_pad(fp, number))


def _clone_pad(number, new):
    def mutate(fp):
        clone = copy.deepcopy(_pad(fp, number))
        clone[1] = new
        first_child(clone, "at")[2] = float(first_child(clone, "at")[2]) + 20
        fp.insert(fp.index(_pad(fp, number)) + 1, clone)

    return mutate


def _renumber(old, new):
    return lambda fp: _pad(fp, old).__setitem__(1, new)


def _resize(number, w, h):
    def mutate(fp):
        size = first_child(_pad(fp, number), "size")
        size[1:3] = [w, h]

    return mutate


def _resize_all(w, h):
    def mutate(fp):
        for pad in children(fp, "pad"):
            first_child(pad, "size")[1:3] = [w, h]

    return mutate


def _move(number, dx=0.0, dy=0.0):
    def mutate(fp):
        at = first_child(_pad(fp, number), "at")
        at[1], at[2] = float(at[1]) + dx, float(at[2]) + dy

    return mutate


def _spread_columns(dx):
    def mutate(fp):
        for pad in children(fp, "pad"):
            at = first_child(pad, "at")
            x = float(at[1])
            at[1] = x + dx if x > 0 else x - dx

    return mutate


def _drop_courtyard(fp):
    for line in children(fp, "fp_line"):
        if first_child(line, "layer")[1] == "F.CrtYd":
            fp.remove(line)


def _shrink_courtyard(fp):
    for line in children(fp, "fp_line"):
        if first_child(line, "layer")[1] == "F.CrtYd":
            for key in ("start", "end"):
                node = first_child(line, key)
                node[1:3] = [float(node[1]) * 0.6, float(node[2]) * 0.6]


def _silk_over_pad(fp):
    fp.append(
        [
            Atom("fp_line"),
            [Atom("start"), -3, -1.905],
            [Atom("end"), 3, -1.905],
            [Atom("stroke"), [Atom("width"), 0.12], [Atom("type"), Atom("solid")]],
            [Atom("layer"), "F.SilkS"],
        ]
    )


PLANTED = [
    ("lm358_soic8", _remove_pad("3"), "footprint.pad_missing"),
    ("lm358_soic8", _clone_pad("3", "99"), "footprint.pad_extra"),
    ("lm358_soic8", _renumber("3", "2"), "footprint.pad_duplicate"),
    ("lm358_soic8", _resize("2", 1.2, 0.6), "footprint.land_mismatch"),
    ("lm358_soic8", _spread_columns(0.3), "footprint.land_mismatch"),
    ("lm358_soic8", _move("2", dy=0.2), "footprint.pitch"),
    ("lm358_soic8", _move("2", dy=-1.27 + 0.05), "footprint.pad_overlap"),
    ("lm358_soic8", _resize_all(0.9, 0.6), "footprint.heel_coverage"),
    ("lm358_soic8", _spread_columns(-0.9), "footprint.toe_coverage"),
    ("lm358_soic8", _resize_all(1.55, 0.3), "footprint.side_coverage"),
    ("lm358_soic8", _drop_courtyard, "footprint.courtyard_missing"),
    ("lm358_soic8", _shrink_courtyard, "footprint.courtyard_small"),
    ("lm358_soic8", _silk_over_pad, "footprint.silk_on_pad"),
    ("tps62130_vqfn16", _resize("17", 1.2, 1.2), "footprint.ep_mismatch"),
    ("tps62130_vqfn16", _move("17", dx=0.5), "footprint.ep_mismatch"),
    ("tps62130_vqfn16", _remove_pad("17"), "footprint.pad_missing"),
]


@pytest.mark.parametrize(
    ("case", "mutate", "expected"),
    PLANTED,
    ids=[f"{e.split('.')[1]}:{m.__qualname__.split('.')[0].strip('_')}" for _, m, e in PLANTED],
)
def test_planted_error_is_detected(case, mutate, expected):
    spec, text = _edit(case, mutate)
    assert expected in _ids(check_footprint(spec, text))


def test_a_tight_pad_gap_is_a_warning_not_a_failure():
    spec, text = _edit("lm358_soic8", _resize_all(1.55, 1.2))  # pads 0.07 mm apart
    findings = check_footprint(spec, text)
    assert "footprint.pad_gap" in _ids(findings, WARN)
    assert "footprint.pad_overlap" not in _ids(findings)


def test_unparseable_and_wrong_root_are_reported():
    spec = _spec("lm358_soic8")
    assert "footprint.unparseable" in _ids(check_footprint(spec, "(footprint (pad"))
    assert "footprint.not_a_footprint" in _ids(check_footprint(spec, "(module)"))


@pytest.mark.skipif(not HAS_KICAD, reason="kicad-cli not installed")
def test_kicad_rejects_a_broken_footprint_file(tmp_path):
    pretty = tmp_path / "lib.pretty"
    pretty.mkdir()
    (pretty / "bad.kicad_mod").write_text('(footprint "bad" (pad "1" smd', encoding="utf-8")
    assert _ids(check_footprint_loads(pretty, name="bad")) & {"kicad.load_failed", "kicad.footprint_not_found"}


@pytest.mark.skipif(not HAS_KICAD, reason="kicad-cli not installed")
def test_a_name_kicad_did_not_export_is_reported(tmp_path):
    spec = _spec("lm358_soic8")
    pretty = tmp_path / "lib.pretty"
    pretty.mkdir()
    (pretty / f"{footprint_name(spec)}.kicad_mod").write_text(render_footprint(spec), encoding="utf-8")
    assert "kicad.footprint_not_found" in _ids(check_footprint_loads(pretty, name="something_else"))


# --------------------------------------------------------------------------- independent oracle

OFFICIAL = Path("/usr/share/kicad/footprints")
ORACLE = {
    "lm358_soic8": OFFICIAL / "Package_SO.pretty" / "SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod",
    "tps62130_vqfn16": OFFICIAL / "Package_DFN_QFN.pretty" / "QFN-16-1EP_3x3mm_P0.5mm_EP1.675x1.675mm.kicad_mod",
}


def _pads_of(text):
    fp = parse_sexpr(text)[0]
    out = {}
    for pad in children(fp, "pad"):
        if pad[1] == "":  # unnumbered paste-only apertures that subdivide an exposed pad
            continue
        x, y = _xy(pad)
        size = first_child(pad, "size")
        out[pad[1]] = (x, y, float(size[1]), float(size[2]))
    return out


def _outer_edge(pad):
    x, y, w, h = pad
    return max(abs(x) + w / 2, abs(y) + h / 2)


@pytest.mark.parametrize("case", SUPPORTED)
def test_layout_agrees_with_the_official_kicad_footprint(case):
    """Land patterns differ by convention, so compare what must agree: numbering, pitch, overall extent."""
    official_path = ORACLE[case]
    if not official_path.is_file():
        pytest.skip("KiCad footprint libraries not installed")
    ours = _pads_of(render_footprint(_spec(case)))
    theirs = _pads_of(official_path.read_text(encoding="utf-8"))
    assert set(ours) == set(theirs)

    def side(value):
        return (value > 0.01) - (value < -0.01)

    for number, pad in ours.items():
        other = theirs[number]
        assert (side(pad[0]), side(pad[1])) == (side(other[0]), side(other[1])), f"pad {number} is on another side"
        if number != "17":  # the exposed pad has no outer edge to compare
            assert abs(_outer_edge(pad) - _outer_edge(other)) <= 0.25, f"pad {number} extent differs"
    assert abs((ours["2"][1] - ours["1"][1]) - (theirs["2"][1] - theirs["1"][1])) < 1e-6  # same pitch
    if "17" in ours:  # the datasheet says 1.68 mm, the official variant is 1.675 mm
        assert abs(ours["17"][2] - theirs["17"][2]) <= 0.05


# --------------------------------------------------------------------------- CLI


def test_cli_build_writes_symbol_and_footprint(tmp_path, capsys):
    spec_path = CASES / "lm358_soic8" / "spec.gold.json"
    assert main(["build", str(spec_path), "--out", str(tmp_path / "out"), "--no-kicad", "--lib-name", "mylib"]) == 0
    report = json.loads(capsys.readouterr().out)
    names = sorted(Path(f).name for f in report["files"])
    assert names == ["LM358.kicad_sym", "SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod"]
    assert (tmp_path / "out" / "mylib.pretty" / "SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod").is_file()
    assert 'property "Footprint" "mylib:SOIC-8_3.9x4.9mm_P1.27mm"' in (tmp_path / "out" / "LM358.kicad_sym").read_text(
        encoding="utf-8"
    )


def test_cli_build_without_a_land_pattern_still_builds_the_symbol(tmp_path, capsys):
    spec_path = CASES / "atmega328p_tqfp32" / "spec.gold.json"
    assert main(["build", str(spec_path), "--out", str(tmp_path / "out"), "--no-kicad"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert [Path(f).name for f in report["files"]] == ["ATmega328P-AU.kicad_sym"]
    assert "footprint.skipped" in {item["id"] for item in report["findings"] if item["status"] == "warn"}
    assert not (tmp_path / "out" / "partspec.pretty").exists()
