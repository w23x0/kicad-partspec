"""Prose rules in ``skills/partspec/reference.md``, asserted as text.

This is a text test on purpose: the rules it guards are instructions to the model reading a
drawing, so there is no code path to exercise. Round r4 found that two runs of the same prompt
read the same callout as three different dimensions and that two golds disagreed over a
parenthesised thickness; these assertions pin the wording that settles both.
"""

import os
import re
from pathlib import Path

REFERENCE = Path(
    os.environ.get("PARTSPEC_REFERENCE_MD")
    or Path(__file__).resolve().parent.parent / "skills" / "partspec" / "reference.md"
)

NAMES = {
    "pitch",
    "body_length",
    "body_width",
    "overall_length",
    "overall_width",
    "height",
    "body_thickness",
    "standoff",
    "lead_width",
    "lead_length",
    "lead_thickness",
    "ep_size",
    "land_pad_length",
    "land_pad_width",
    "land_span",
    "land_ep_size",
}


def _section():
    """The `## Dimension names` section, whitespace-collapsed and lower-cased."""
    body = REFERENCE.read_text(encoding="utf-8")
    start = body.index("## Dimension names")
    end = body.index("\n## ", start + 1) if "\n## " in body[start + 1 :] else len(body)
    return re.sub(r"\s+", " ", body[start:end]).lower()


def _rows(first_table_only=True):
    """Table rows of the section as lower-cased cell pairs, the dimension table first."""
    lines = REFERENCE.read_text(encoding="utf-8").splitlines()
    tables = []
    table = []
    for line in lines[lines.index("## Dimension names") :]:
        if line.startswith("|"):
            table.append(line)
        elif table:
            tables.append(table)
            table = []
    if table:
        tables.append(table)
    if first_table_only:
        tables = tables[:1]
    rows = []
    for table in tables:
        for line in table:
            cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
            if len(cells) == 2 and cells[0] and not set(cells[0]) <= set("-: "):
                rows.append((cells[0], cells[1]))
    return rows


def _span_row(name):
    """The row of the spans table that names `name`: the drawing feature, then the name."""
    rows = [first for first, second in _rows(first_table_only=False) if second.strip(" `") == name]
    assert rows, f"no table row names {name} by the span it measures"
    return " ".join(rows)


def test_every_dimension_name_is_still_defined():
    """Regression guard: the section keeps defining exactly the names it defined before."""
    first_cell_names = set()
    for first, _ in _rows():
        first_cell_names.update(re.findall(r"`([a-z_]+)`", first))
    assert first_cell_names == NAMES


def test_standoff_spans_body_underside_to_seating_plane():
    row = _span_row("standoff")
    assert "body underside" in row
    assert "seating" in row


def test_lead_thickness_is_the_callout_across_the_cross_section():
    row = _span_row("lead_thickness")
    assert "cross-section" in row
    assert "edge" in row


def test_lead_length_runs_from_the_lead_tip_to_the_foot():
    row = _span_row("lead_length")
    assert "lead tip" in row
    assert "board" in row


def test_a_callout_is_named_by_the_planes_it_spans():
    text = _section()
    assert "extension lines run between" in text
    assert "re-render the page" in text
    assert "which of these three" in text


def test_parenthesised_value_is_not_a_package_dimension():
    text = _section()
    assert "reference dimensions" in text
    assert "land_*" in text
    assert "must not become a package dimension" in text


def test_boxed_basic_value_is_not_a_package_dimension():
    text = _section()
    assert "basic`" in text
    assert "land pattern" in text
