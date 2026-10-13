"""The audit board's counting logic in ``scripts/audit.py``.

`./scripts/audit.sh` is the project's only progress signal (AGENTS.md). What it counts is
therefore load-bearing: a rule whose test was skipped must not be reported as passing, an
uncovered rule must not be reported as anything, and a regression must be visible. These
tests call the board computation directly, with the statuses a rule test run can return.
"""

import importlib.util
from pathlib import Path

import pytest

AUDIT = Path(__file__).resolve().parent.parent / "scripts" / "audit.py"

_spec = importlib.util.spec_from_file_location("audit_board", AUDIT)
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)

RULES = [
    {"id": "SCH-001", "level": "MUST", "statement": "every value cites a page and a quote", "spec": "skills/partspec/reference.md"},
    {"id": "SCH-005", "level": "MUST", "statement": "dimension values are ordered and positive", "spec": "skills/partspec/reference.md"},
    {"id": "DIM-001", "level": "SHOULD", "statement": "a dimension gets the min/nom/max the sheet prints", "spec": "skills/partspec/reference.md"},
    {"id": "GEN-001", "level": "MUST", "statement": "golds build and load", "spec": "src/kicad_partspec/api.py · build", "suite": "gold-build"},
]
SUITES = {"gold-spec": (True, "23/23", 23), "gold-quotes": (True, "skipped", None), "gold-build": (True, "23/23", None)}


def board(statuses, suites=None, previous=None):
    return audit._board(RULES, statuses, SUITES if suites is None else suites, previous or {})


def test_a_passing_rule_counts_as_passing():
    result = board({"SCH-005": "PASSED", "GEN-001": "PASSED"})
    assert result["passing"] == ["SCH-005", "GEN-001"]


def test_a_failing_rule_fails_instead_of_passing():
    result = board({"SCH-005": "FAILED", "GEN-001": "PASSED"})
    assert result["failing"] == ["SCH-005"]
    assert result["passing"] == ["GEN-001"]


def test_a_failing_rule_is_a_regression_against_the_state_file():
    result = board({"SCH-005": "FAILED"}, previous={"rules": {"SCH-005": "pass"}})
    assert result["regressed"] == ["SCH-005"]


def test_a_suite_that_was_green_and_is_not_is_a_regression():
    suites = dict(SUITES, **{"gold-spec": (False, "22/23", 23)})
    result = board({"SCH-005": "PASSED"}, suites=suites, previous={"suites": {"gold-spec": True}})
    assert result["regressed"] == ["gold-spec"]


def test_a_rule_whose_test_was_skipped_is_nothing():
    """The defect this file exists for: a SKIPPED test used to be counted in 通过 and kept
    out of 未覆盖, so a rule AGENTS.md allows to skip on a missing environment would report
    as progress that never ran."""
    result = board({"SCH-005": "SKIPPED", "GEN-001": "PASSED"})
    assert result["skipped"] == ["SCH-005"]
    assert result["covered"] == ["SCH-005", "GEN-001"]
    assert result["passing"] == ["GEN-001"]
    assert result["uncovered"] == ["SCH-001", "DIM-001"]


def test_a_rule_with_no_test_and_no_suite_is_uncovered_and_never_passing():
    result = board({"SCH-001": "PASSED"})
    assert result["uncovered"] == ["SCH-005", "DIM-001"]
    assert result["passing"] == ["SCH-001", "GEN-001"]
    assert result["skipped"] == []


@pytest.mark.parametrize("status", ["PASSED", "FAILED"])
def test_a_rule_backed_by_a_gold_suite_needs_no_test_of_its_own(status):
    """GEN-001 is covered by the gold-build suite, so its counting follows the suite."""
    result = board({"GEN-001": status})
    assert result["covered"] == ["GEN-001"]
    assert result["passing"] == (["GEN-001"] if status == "PASSED" else [])
