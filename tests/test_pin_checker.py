"""Tests for deplint.pin_checker."""

import pytest
from deplint.parser import Dependency
from deplint.pin_checker import check_pins, PinIssue, PinCheckResult


def make_dep(name: str, spec: str = "") -> Dependency:
    return Dependency(name=name, version_spec=spec, extras=[])


def test_no_issues_with_exact_pins():
    deps = [make_dep("requests", "==2.28.0"), make_dep("flask", "==2.3.1")]
    result = check_pins(deps)
    assert not result.has_issues()


def test_no_issues_with_empty_list():
    result = check_pins([])
    assert not result.has_issues()


def test_detects_missing_version():
    deps = [make_dep("requests")]
    result = check_pins(deps)
    assert result.has_issues()
    assert result.issues[0].package == "requests"
    assert "No version specified" in result.issues[0].reason


def test_detects_open_upper_bound():
    deps = [make_dep("django", ">=3.2")]
    result = check_pins(deps)
    assert result.has_issues()
    assert "upper bound" in result.issues[0].reason


def test_no_issue_for_bounded_range():
    deps = [make_dep("django", ">=3.2,<4.0")]
    result = check_pins(deps)
    assert not result.has_issues()


def test_detects_strict_greater_than():
    deps = [make_dep("numpy", ">1.20")]
    result = check_pins(deps)
    assert result.has_issues()
    assert "greater-than" in result.issues[0].reason


def test_compatible_release_no_issue():
    deps = [make_dep("boto3", "~=1.26")]
    result = check_pins(deps)
    assert not result.has_issues()


def test_multiple_issues_collected():
    deps = [
        make_dep("requests"),
        make_dep("flask", ">=2.0"),
        make_dep("click", "==8.1.3"),
    ]
    result = check_pins(deps)
    assert len(result.issues) == 2


def test_str_no_issues():
    result = PinCheckResult(issues=[])
    assert "No pin issues" in str(result)


def test_str_with_issues():
    result = PinCheckResult(issues=[PinIssue("requests", "", "No version specified")])
    output = str(result)
    assert "Pin issues detected" in output
    assert "requests" in output


def test_issue_str():
    issue = PinIssue("flask", ">=2.0", "Open upper bound")
    s = str(issue)
    assert "flask" in s
    assert ">=2.0" in s
    assert "Open upper bound" in s
