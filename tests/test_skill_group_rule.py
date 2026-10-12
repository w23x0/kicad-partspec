"""Guards the round-4 finding: the `group` rule in the skill's reference was misread by three
rounds and three hand-written golds alike — unit letters read as a requirement, a channel's two
pins split apart, and a rail shared by all units treated as an alternative to grouping the units.
"""

import re
from pathlib import Path

REFERENCE = Path(__file__).resolve().parent.parent / "skills" / "partspec" / "reference.md"


def _flat(text):
    """Lower-cased with the whitespace collapsed, so an assertion ignores line wrapping."""
    return re.sub(r"\s+", " ", text.lower())


def _group_rule(text):
    """The `group` bullet of ## Pin fields, the supply-pins bullet and the shared-node carve-out, flattened."""
    bullet = re.search(r"^- `group`:.*?(?=^- `|\Z)", text, re.MULTILINE | re.DOTALL)
    assert bullet, "no `group` bullet in ## Pin fields"
    supply = re.search(
        r"^- The supply pins are the one exception.*?(?=^- \`|\Z)", text, re.MULTILINE | re.DOTALL
    )
    carve_out = re.search(r"^- A node shared by every unit.*?(?=^- \`|\Z)", text, re.MULTILINE | re.DOTALL)
    return _flat(
        bullet.group(0)
        + "\n"
        + (supply.group(0) if supply else "")
        + "\n"
        + (carve_out.group(0) if carve_out else "")
    )


RULE = _group_rule(REFERENCE.read_text(encoding="utf-8"))


def test_grouping_is_required_for_repeated_units():
    assert re.search(r"required whenever the datasheet shows repeated, identical functional blocks", RULE)
    assert re.search(r"every pin of every unit is grouped", RULE)
    assert re.search(r"leaving them ungrouped is a defect", RULE)


def test_the_key_is_the_datasheets_own_label_for_the_unit():
    assert re.search(r"key is whatever the datasheet calls the unit", RULE)
    assert re.search(r"channel numbers", RULE)
    assert re.search(r"channel names", RULE)
    assert re.search(r"never a key the datasheet does not use", RULE)
    assert re.search(r"numbered or named channel is a channel even without a letter", RULE)


def test_both_pins_of_one_unit_share_one_key():
    assert re.search(r"both pins of one unit share that one key", RULE)
    assert re.search(r"base and the collector of one channel", RULE)


def test_power_is_in_addition_to_the_unit_groups():
    assert re.search(r"common to all units", RULE)
    assert re.search(r"common emitter, a shared rail", RULE)
    assert re.search(r"in addition to a unit group", RULE)
    assert re.search(r"never instead of it", RULE)
    assert re.search(r"pwr` cell in a type column", RULE)
    assert re.search(r"grouping it `\"power\"` is optional", RULE)


def test_a_node_shared_by_every_unit_is_not_thereby_a_supply():
    """ULN2003A's COM: shared by all seven channels, yet passive — the datasheet says the part needs no supply."""
    assert re.search(r"node shared by every unit is not thereby a supply", RULE)
    assert re.search(r"this device does not need a power supply", RULE)
    assert re.search(r"may float in resistive-load drive", RULE)


def test_two_sides_of_a_function_stays_scoped_to_different_blocks():
    assert re.search(r"two sides of one part's function are different blocks, not units", RULE)
    assert re.search(r"the a port and b port of a level translator", RULE)
    assert re.search(r"does not split the two pins of one unit", RULE)


def test_single_instance_pins_stay_ungrouped():
    assert re.search(r"pins with no unit of their own", RULE)
    assert re.search(r"address pin, a reset, a chip select", RULE)
