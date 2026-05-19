"""Tests for deplint.circular_checker."""
import pytest
from deplint.circular_checker import check_circular, CircularCheckResult


class _Dep:
    def __init__(self, name: str, line_number: int = 1):
        self.name = name
        self.line_number = line_number


def make_dep(name: str, line: int = 1) -> _Dep:
    return _Dep(name, line)


# ---------------------------------------------------------------------------
# Basic cases
# ---------------------------------------------------------------------------

def test_no_issues_with_empty_list():
    result = check_circular([])
    assert not result.has_issues()


def test_no_issues_with_normal_packages():
    deps = [make_dep("requests"), make_dep("flask"), make_dep("django")]
    result = check_circular(deps)
    assert not result.has_issues()


def test_detects_setuptools():
    result = check_circular([make_dep("setuptools", line=3)])
    assert result.has_issues()
    assert result.issues[0].package == "setuptools"
    assert result.issues[0].line_number == 3


def test_detects_pip():
    result = check_circular([make_dep("pip", line=7)])
    assert result.has_issues()
    assert result.issues[0].package == "pip"


def test_detects_wheel():
    result = check_circular([make_dep("wheel")])
    assert result.has_issues()
    assert "build backend" in result.issues[0].detail


def test_detects_distribute():
    result = check_circular([make_dep("distribute")])
    assert result.has_issues()


def test_case_insensitive_detection():
    result = check_circular([make_dep("SetupTools")])
    assert result.has_issues()


def test_hyphen_normalisation():
    # 'pip' has no hyphen variant but distribute-style names should normalise
    result = check_circular([make_dep("Distribute")])
    assert result.has_issues()


def test_multiple_circular_deps():
    deps = [make_dep("requests"), make_dep("pip", 2), make_dep("wheel", 5)]
    result = check_circular(deps)
    assert len(result.issues) == 2


def test_str_no_issues():
    result = CircularCheckResult()
    assert "no issues" in str(result)


def test_str_with_issues():
    deps = [make_dep("pip", 4)]
    result = check_circular(deps)
    text = str(result)
    assert "pip" in text
    assert "Line 4" in text
    assert "CircularCheck issues:" in text
