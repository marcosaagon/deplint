"""Tests for the environment marker checker."""

import pytest
from deplint.marker_checker import (
    check_markers,
    MarkerCheckResult,
    MarkerIssue,
)


def make_dep(name, marker=None, line_number=1):
    """Helper to create a minimal Dependency-like object."""

    class Dep:
        pass

    d = Dep()
    d.name = name
    d.marker = marker
    d.line_number = line_number
    return d


def test_no_issues_with_empty_list():
    result = check_markers([])
    assert not result.has_issues()


def test_no_issues_when_no_markers():
    deps = [make_dep("requests"), make_dep("flask")]
    result = check_markers(deps)
    assert not result.has_issues()


def test_no_issues_with_known_markers():
    deps = [
        make_dep("requests", marker='python_version >= "3.8"'),
        make_dep("pywin32", marker='sys_platform == "win32"'),
        make_dep("uvloop", marker='platform_system != "Windows"'),
    ]
    result = check_markers(deps)
    assert not result.has_issues()


def test_detects_unknown_marker_name():
    deps = [make_dep("requests", marker='fake_marker == "value"', line_number=5)]
    result = check_markers(deps)
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "requests"
    assert result.issues[0].line_number == 5
    assert "fake_marker" in result.issues[0].reason


def test_detects_empty_marker():
    deps = [make_dep("flask", marker="   ", line_number=3)]
    result = check_markers(deps)
    assert result.has_issues()
    assert "empty" in result.issues[0].reason


def test_multiple_unknown_markers():
    deps = [
        make_dep("pkg-a", marker='bad_marker == "x"', line_number=2),
        make_dep("pkg-b", marker='another_bad == "y"', line_number=7),
    ]
    result = check_markers(deps)
    assert len(result.issues) == 2


def test_mixed_valid_and_invalid_markers():
    deps = [
        make_dep("requests", marker='python_version >= "3.8"'),
        make_dep("legacy", marker='custom_env == "prod"', line_number=4),
    ]
    result = check_markers(deps)
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "legacy"


def test_str_no_issues():
    result = MarkerCheckResult(issues=[])
    assert "No marker issues" in str(result)


def test_str_with_issues():
    issue = MarkerIssue(
        package="mypkg",
        line_number=10,
        marker='bad_var == "1"',
        reason="unknown marker name 'bad_var'",
    )
    result = MarkerCheckResult(issues=[issue])
    output = str(result)
    assert "mypkg" in output
    assert "10" in output
    assert "bad_var" in output


def test_issue_str_format():
    issue = MarkerIssue(
        package="django",
        line_number=15,
        marker='os_type == "linux"',
        reason="unknown marker name 'os_type'",
    )
    text = str(issue)
    assert "django" in text
    assert "15" in text
    assert "os_type" in text
