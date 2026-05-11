"""Tests for the requirements.txt parser."""

import pytest
from deplint.parser import Dependency, parse_requirements


SAMPLE_REQUIREMENTS = """
# This is a comment
requests>=2.28.0,<3.0
flask==2.3.2
numpy
pandas[excel,plot]>=1.5
-r other-requirements.txt
--index-url https://pypi.org/simple

# Another comment
click>=8.0  # inline comment
"""


def test_parse_basic_dependency():
    deps = parse_requirements("requests>=2.28.0")
    assert len(deps) == 1
    dep = deps[0]
    assert dep.name == "requests"
    assert dep.version_spec == ">=2.28.0"
    assert dep.extras == []


def test_parse_pinned_version():
    deps = parse_requirements("flask==2.3.2")
    assert deps[0].version_spec == "==2.3.2"


def test_parse_no_version():
    deps = parse_requirements("numpy")
    assert deps[0].name == "numpy"
    assert deps[0].version_spec == ""


def test_parse_extras():
    deps = parse_requirements("pandas[excel,plot]>=1.5")
    dep = deps[0]
    assert dep.name == "pandas"
    assert dep.extras == ["excel", "plot"]
    assert dep.version_spec == ">=1.5"


def test_skip_comments_and_blank_lines():
    content = "\n# comment\n\nrequests>=1.0\n"
    deps = parse_requirements(content)
    assert len(deps) == 1


def test_skip_pip_options():
    content = "-r base.txt\n--index-url https://example.com\nflask==1.0"
    deps = parse_requirements(content)
    assert len(deps) == 1
    assert deps[0].name == "flask"


def test_inline_comment_ignored():
    deps = parse_requirements("click>=8.0  # inline comment")
    assert deps[0].name == "click"
    assert deps[0].version_spec == ">=8.0"


def test_line_number_tracking():
    content = "requests>=1.0\nflask==2.0"
    deps = parse_requirements(content)
    assert deps[0].line_number == 1
    assert deps[1].line_number == 2


def test_full_sample():
    deps = parse_requirements(SAMPLE_REQUIREMENTS)
    names = [d.name for d in deps]
    assert "requests" in names
    assert "flask" in names
    assert "numpy" in names
    assert "pandas" in names
    assert "click" in names
    assert len(deps) == 5


def test_dependency_str():
    dep = Dependency(name="requests", version_spec=">=2.0", extras=["security"])
    assert str(dep) == "requests[security]>=2.0"
