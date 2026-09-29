"""Metadata that must stay true for a release."""

import re
from pathlib import Path

import pytest

import kicad_partspec

# tomllib is standard from Python 3.11; the metadata only needs checking once, on a newer interpreter.
tomllib = pytest.importorskip("tomllib")

ROOT = Path(__file__).resolve().parent.parent
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]


def test_the_two_version_numbers_agree():
    assert PROJECT["version"] == kicad_partspec.__version__


def test_the_release_tag_rule_matches_the_package_version_format():
    assert re.fullmatch(r"\d+\.\d+\.\d+", PROJECT["version"])


def test_pre_alpha_is_declared_and_metadata_is_complete():
    assert "Development Status :: 2 - Pre-Alpha" in PROJECT["classifiers"]
    assert PROJECT["authors"] and PROJECT["keywords"]
    assert {"Homepage", "Repository", "Issues"} <= set(PROJECT["urls"])
    assert all(url.startswith("https://github.com/w23x0/kicad-partspec") for url in PROJECT["urls"].values())


def test_no_personal_contact_data_is_published_in_the_metadata():
    for author in PROJECT["authors"]:
        assert "email" not in author


def test_declared_python_versions_match_requires_python():
    minimum = int(PROJECT["requires-python"].removeprefix(">=3.").split(",")[0])
    declared = {c.rsplit(" ", 1)[1] for c in PROJECT["classifiers"] if re.search(r"Python :: 3\.\d+$", c)}
    assert min(int(v.removeprefix("3.")) for v in declared) == minimum


def test_readme_links_work_on_pypi():
    """PyPI renders README.md away from the repository, so relative links would break."""
    for target in re.findall(r"\]\(([^)]+)\)", (ROOT / "README.md").read_text(encoding="utf-8")):
        assert target.startswith("https://"), f"relative link in README: {target}"


def test_dependencies_stay_optional():
    assert PROJECT["dependencies"] == []
    assert "mcp" in PROJECT["optional-dependencies"]
