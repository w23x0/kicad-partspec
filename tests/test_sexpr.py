import pytest

from kicad_partspec.sexpr import as_float, as_int, children, first_child, parse_sexpr, scalar_child

SAMPLE = '(kicad_symbol_lib (version 20241209) (symbol "U1" (property "Value" "a \\"b\\"") (pin passive line)))'


def test_parse_nested_and_helpers():
    tree = parse_sexpr(SAMPLE)
    lib = tree[0]
    assert lib[0] == "kicad_symbol_lib"
    assert scalar_child(lib, "version") == "20241209"
    symbol = first_child(lib, "symbol")
    assert symbol[1] == "U1"
    assert scalar_child(first_child(symbol, "property"), "Value") is None  # value is positional, not a child
    assert children(symbol, "pin")[0][1] == "passive"


def test_escaped_quote_is_decoded():
    tree = parse_sexpr('(a "x \\"y\\"")')
    assert tree[0][1] == 'x "y"'


def test_semicolon_comment_is_skipped():
    assert parse_sexpr("(a 1) ; trailing\n(b 2)") == [["a", "1"], ["b", "2"]]


@pytest.mark.parametrize("text", ["(a", "a)", '(a "unterminated)'])
def test_malformed_input_is_rejected(text):
    with pytest.raises(ValueError):
        parse_sexpr(text)


def test_depth_limit():
    with pytest.raises(ValueError, match="depth limit"):
        parse_sexpr("(" * 5 + ")" * 5, max_depth=3)


def test_token_limit():
    with pytest.raises(ValueError, match="token limit"):
        parse_sexpr("(a b c d e f)", max_tokens=3)


def test_number_helpers():
    assert as_float("1.5") == 1.5
    assert as_float("nan") is None
    assert as_int("+12") == 12
    assert as_int("1.5") is None
    assert as_int(True) is None
