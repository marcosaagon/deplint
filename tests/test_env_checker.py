"""Tests for deplint.env_checker."""
import pytest
from deplint.env_checker import check_env_markers, EnvConflict


class Dep:
    """Minimal dependency stub."""
    def __init__(self, name, marker=None, line_number=1):
        self.name = name
        self.marker = marker
        self.line_number = line_number


def make_dep(name, marker=None, line_number=1):
    return Dep(name=name, marker=marker, line_number=line_number)


def test_no_issues_with_empty_list():
    result = check_env_markers([])
    assert not result.has_issues()


def test_no_issues_when_no_markers():
    deps = [make_dep("requests"), make_dep("flask")]
    result = check_env_markers(deps)
    assert not result.has_issues()


def test_no_issues_with_valid_range_marker():
    deps = [make_dep("pywin32", marker='sys_platform == "win32"')]
    result = check_env_markers(deps)
    assert not result.has_issues()


def test_no_issues_with_python_version_range():
    deps = [make_dep("typing", marker='python_version >= "3.5"')]
    result = check_env_markers(deps)
    assert not result.has_issues()


def test_detects_hardcoded_python_version_eq():
    deps = [make_dep("oldlib", marker='python_version == "3.6"', line_number=5)]
    result = check_env_markers(deps)
    assert result.has_issues()
    assert len(result.conflicts) == 1
    conflict = result.conflicts[0]
    assert conflict.package == "oldlib"
    assert conflict.line_number == 5
    assert "==" in conflict.marker


def test_detects_unknown_marker_key():
    deps = [make_dep("weirdpkg", marker='custom_env == "production"', line_number=3)]
    result = check_env_markers(deps)
    assert result.has_issues()
    assert "unknown marker key" in result.conflicts[0].reason


def test_multiple_deps_mixed_issues():
    deps = [
        make_dep("safe", marker='sys_platform == "linux"'),
        make_dep("pinned", marker='python_version == "3.8"', line_number=2),
        make_dep("weird", marker='custom_key == "foo"', line_number=4),
    ]
    result = check_env_markers(deps)
    assert result.has_issues()
    assert len(result.conflicts) == 2
    packages = {c.package for c in result.conflicts}
    assert packages == {"pinned", "weird"}


def test_str_no_issues():
    result = check_env_markers([])
    assert "No environment marker conflicts" in str(result)


def test_str_with_issues():
    deps = [make_dep("oldlib", marker='python_version == "3.6"', line_number=7)]
    result = check_env_markers(deps)
    output = str(result)
    assert "oldlib" in output
    assert "Line 7" in output


def test_conflict_str():
    conflict = EnvConflict(
        package="foo",
        line_number=10,
        marker='python_version == "3.7"',
        reason="hard-coded '==' python version marker may break on other interpreters",
    )
    s = str(conflict)
    assert "foo" in s
    assert "Line 10" in s
    assert "hard-coded" in s


def test_python_full_version_eq_flagged():
    deps = [make_dep("legacy", marker='python_full_version == "3.6.9"', line_number=1)]
    result = check_env_markers(deps)
    assert result.has_issues()
    assert result.conflicts[0].package == "legacy"
