"""Tests for the Python version compatibility checker."""
import pytest
from deplint.python_version_checker import (
    check_python_version_compatibility,
    PythonVersionIssue,
    PythonVersionCheckResult,
)
from deplint.parser import Dependency


def make_dep(name: str, spec: str = "", line: int = 1) -> Dependency:
    return Dependency(name=name, version_spec=spec, extras=[], line_number=line)


CUSTOM_MAP = {
    "newlib": ">=3.10",
    "oldlib": ">=3.6",
    "midlib": ">=3.8",
}


def test_no_issues_with_empty_list():
    result = check_python_version_compatibility([], package_python_map=CUSTOM_MAP)
    assert not result.has_issues()


def test_no_issues_when_package_not_in_map():
    deps = [make_dep("unknownpkg")]
    result = check_python_version_compatibility(deps, package_python_map=CUSTOM_MAP)
    assert not result.has_issues()


def test_no_issues_when_python_version_sufficient():
    deps = [make_dep("newlib")]
    result = check_python_version_compatibility(
        deps, current_python="3.11", package_python_map=CUSTOM_MAP
    )
    assert not result.has_issues()


def test_detects_incompatible_package():
    deps = [make_dep("newlib")]
    result = check_python_version_compatibility(
        deps, current_python="3.9", package_python_map=CUSTOM_MAP
    )
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "newlib"
    assert "3.10" in result.issues[0].required_python


def test_detects_multiple_incompatible_packages():
    deps = [make_dep("newlib"), make_dep("midlib")]
    result = check_python_version_compatibility(
        deps, current_python="3.7", package_python_map=CUSTOM_MAP
    )
    assert result.has_issues()
    assert len(result.issues) == 2


def test_compatible_package_not_flagged():
    deps = [make_dep("oldlib"), make_dep("newlib")]
    result = check_python_version_compatibility(
        deps, current_python="3.9", package_python_map=CUSTOM_MAP
    )
    assert result.has_issues()
    names = [i.package for i in result.issues]
    assert "oldlib" not in names
    assert "newlib" in names


def test_issue_str_includes_line_number():
    issue = PythonVersionIssue(package="newlib", required_python=">=3.10", line_number=5)
    assert "line 5" in str(issue)
    assert "newlib" in str(issue)
    assert "3.10" in str(issue)


def test_issue_str_without_line_number():
    issue = PythonVersionIssue(package="newlib", required_python=">=3.10")
    assert "line" not in str(issue)


def test_result_str_no_issues():
    result = PythonVersionCheckResult(issues=[])
    assert "OK" in str(result)


def test_result_str_with_issues():
    result = PythonVersionCheckResult(
        issues=[PythonVersionIssue(package="newlib", required_python=">=3.10")]
    )
    assert "newlib" in str(result)
    assert "issues" in str(result).lower()


def test_case_insensitive_lookup():
    deps = [make_dep("NewLib")]
    result = check_python_version_compatibility(
        deps, current_python="3.9", package_python_map=CUSTOM_MAP
    )
    assert result.has_issues()
    assert result.issues[0].package == "NewLib"
