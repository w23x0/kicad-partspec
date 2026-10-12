"""Prose rules in ``skills/partspec/reference.md``, asserted as text.

This is a text test on purpose: the rules it guards are instructions to the model reading a
drawing, so there is no code path to exercise. Round r4 found that two runs of the same prompt
read the same callout as three different dimensions and that two golds disagreed over a
parenthesised thickness; these assertions pin the wording that settles both.

Behaviour-level conformance for these rules (the golds obeying them, the checkers rejecting the
violations) lives in ``tests/test_rules.py`` under rule-ids.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = (ROOT / "skills" / "partspec" / "reference.md").read_text(encoding="utf-8")
SKILL = (ROOT / "skills" / "partspec" / "SKILL.md").read_text(encoding="utf-8")
README = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")


def _flat(text):
    """Prose with its line wrapping undone, so an assertion does not depend on where a line broke."""
    return " ".join(text.split())


def _bullet(text, start):
    """The `- ` bullet in `text` that begins with `start`, unwrapped to one line."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("- ") and start in line:
            block = [line]
            for follow in lines[i + 1 :]:
                if follow.startswith("  ") and follow.strip():
                    block.append(follow.strip())
                else:
                    break
            return _flat(" ".join(block))
    raise AssertionError(f"no bullet starting {start!r} in the skill prose")


# --- the rules themselves -------------------------------------------------------------------------------


def test_mpn_is_the_datasheets_own_orderable():
    assert "manufacturer part number as it should appear in KiCad" not in REFERENCE
    assert "manufacturer part number as the datasheet prints it" in REFERENCE
    flat = _flat(REFERENCE)
    assert re.search(r"`mpn` is that string copied exactly", flat)
    assert re.search(r"not a package-only form that appears on no page", flat)


def test_sibling_part_names_never_become_alt_names():
    for prose in (SKILL, REFERENCE):
        flat = _flat(prose)
        assert "sibling part" in flat
        assert re.search(r"leave `alt_names` empty", flat)
    assert "`alt_names` entry is another function of the same pad" in _flat(REFERENCE)


def test_power_group_rule_is_permissive_for_a_lone_supply():
    rule = _bullet(REFERENCE, "The supply pins are the one exception")
    assert "as a block of their own" in rule
    assert "PWR" in rule
    # The rule may not become a blanket mandate for every supply or ground pin: the adjudication
    # allowed either way on exactly those, and thirteen golds rely on that.
    assert not re.search(r'Group `"power"` (?:any|every) pin', rule)
    assert "optional" in rule


def test_callout_naming_guidance_is_present():
    flat = _flat(REFERENCE)
    assert "extension lines" in flat
    assert "GAGE PLANE" in flat
    assert "DETAIL A" in flat
    for name in ("overall_width", "body_length", "body_width", "overall_length"):
        assert name in flat


def test_land_dimensions_are_metal_not_the_mask_opening():
    flat = _flat(REFERENCE)
    assert "SOLDER MASK OPENING" in flat
    assert re.search(r"`land_span`.* are metal", flat)


def test_body_to_tip_lead_length_rule_is_not_vendor_specific():
    table = _flat(REFERENCE[REFERENCE.index("| the tip-to-tip `E`") :])
    assert "any vendor's drawing" in table
    assert "is not our `lead_length`" in table


def test_evals_readme_carries_no_blanket_dimension_convention():
    flat = _flat(README)
    assert "leave those dimensions out instead of guessing" not in flat
    assert ".004-.010" not in flat
    assert "a convention in this file is never a rule an extraction run is graded against" in flat
