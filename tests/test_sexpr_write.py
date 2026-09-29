import shutil
from pathlib import Path

import pytest

from partspec.sexpr import Atom, format_number, parse_sexpr, write_sexpr

OFFICIAL_LIBS = Path("/usr/share/kicad/symbols")


@pytest.mark.parametrize(
    ("value", "text"),
    [(2.54, "2.54"), (-7.62, "-7.62"), (0.0, "0"), (-0.0, "0"), (3, "3"), (1.0, "1"), (0.1 + 0.2, "0.3"), (1e-9, "0")],
)
def test_format_number(value, text):
    assert format_number(value) == text


@pytest.mark.parametrize("bad", [True, float("nan"), float("inf")])
def test_format_number_rejects_non_values(bad):
    with pytest.raises((TypeError, ValueError)):
        format_number(bad)


def test_strings_are_quoted_and_atoms_are_not():
    text = write_sexpr([Atom("property"), 'a "b" \\c', Atom("yes"), 1.5])
    assert text == '(property "a \\"b\\" \\\\c" yes 1.5)\n'
    assert parse_sexpr(text)[0][1] == 'a "b" \\c'


def test_nested_layout_matches_kicad_style():
    tree = [Atom("a"), [Atom("b"), 1, 2], [Atom("c"), [Atom("d"), Atom("yes")]]]
    assert write_sexpr(tree) == "(a\n\t(b 1 2)\n\t(c\n\t\t(d yes)\n\t)\n)\n"


def test_unwritable_value_is_a_type_error():
    with pytest.raises(TypeError):
        write_sexpr([Atom("a"), object()])
    with pytest.raises(TypeError):
        write_sexpr("not a list")  # type: ignore[arg-type]


def test_parser_distinguishes_quoted_from_bare():
    tree = parse_sexpr('(a "b" c 1)')[0]
    assert [type(item) is Atom for item in tree] == [True, False, True, True]


@pytest.mark.skipif(not OFFICIAL_LIBS.is_dir(), reason="KiCad symbol libraries not installed")
@pytest.mark.parametrize("name", ["Amplifier_Operational", "Regulator_Linear", "Device"])
def test_official_library_roundtrips(name):
    path = OFFICIAL_LIBS / f"{name}.kicad_sym"
    if not path.is_file() or path.stat().st_size > 3_000_000:
        pytest.skip("library missing or over the parser's token budget")
    tree = parse_sexpr(path.read_text(encoding="utf-8"))
    assert parse_sexpr(write_sexpr(tree[0])) == tree


@pytest.mark.skipif(shutil.which("kicad-cli") is None, reason="kicad-cli not installed")
def test_written_tree_is_loadable_by_kicad(tmp_path):
    source = (OFFICIAL_LIBS / "Amplifier_Operational.kicad_sym").read_text(encoding="utf-8")
    target = tmp_path / "rewritten.kicad_sym"
    target.write_text(write_sexpr(parse_sexpr(source)[0]), encoding="utf-8")
    from partspec.kicad import cli

    result = cli.run_cli([cli.CLI_COMMAND, "sym", "export", "svg", "-o", str(tmp_path), str(target)], timeout=300)
    assert result.returncode == 0
