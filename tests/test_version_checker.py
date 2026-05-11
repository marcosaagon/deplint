"""Tests for the version conflict checker."""

import pytest
from deplint.parser import Dependency
from deplint.version_checker import (
    CheckResult,
    VersionConflict,
    check_version_conflicts,
)


def make_dep(name: str, version_spec: str = "", extras=None) -> Dependency:
    return Dependency(name=name, version_spec=version_spec, extras=extras or [])


def test_no_conflicts_empty_list():
    result = check_version_conflicts([])
    assert not result.has_conflicts


def test_no_conflicts_valid_deps():
    deps = [
        make_dep("requests", ">=2.0,<3.0"),
        make_dep("flask", "==2.3.1"),
    ]
    result = check_version_conflicts(deps)
    assert not result.has_conflicts


def test_detects_duplicate_package():
    deps = [
        make_dep("requests", ">=2.0"),
        make_dep("requests", "==2.28.0"),
    ]
    result = check_version_conflicts(deps)
    assert result.has_conflicts
    assert any("multiple times" in c.message for c in result.conflicts)


def test_duplicate_package_case_insensitive():
    deps = [
        make_dep("Django", ">=3.0"),
        make_dep("django", "==4.2"),
    ]
    result = check_version_conflicts(deps)
    assert result.has_conflicts


def test_detects_contradictory_specifier():
    deps = [make_dep("numpy", ">=2.0,<1.5")]
    result = check_version_conflicts(deps)
    assert result.has_conflicts
    assert any("numpy" in c.package for c in result.conflicts)


def test_no_version_spec_no_conflict():
    deps = [make_dep("boto3")]
    result = check_version_conflicts(deps)
    assert not result.has_conflicts


def test_check_result_str_no_conflicts():
    result = CheckResult()
    assert "No version conflicts" in str(result)


def test_check_result_str_with_conflicts():
    conflict = VersionConflict(
        package="requests",
        specifiers=[">=2.0", "==1.0"],
        message="package declared multiple times",
    )
    result = CheckResult(conflicts=[conflict])
    output = str(result)
    assert "[version-conflict]" in output
    assert "requests" in output


def test_version_conflict_str():
    conflict = VersionConflict(
        package="flask",
        specifiers=[">=2.0,<1.0"],
        message="lower bound is not compatible with upper bound",
    )
    assert "[version-conflict]" in str(conflict)
    assert "flask" in str(conflict)
