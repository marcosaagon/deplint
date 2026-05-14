"""Tests for the outdated package checker."""
import pytest
from deplint.parser import Dependency
from deplint.outdated_checker import (
    OutdatedIssue,
    OutdatedCheckResult,
    check_outdated,
    _extract_pinned_version,
)


def make_dep(name: str, *specs: str) -> Dependency:
    return Dependency(name=name, version_specs=list(specs), extras=[])


def make_info(version: str) -> dict:
    return {"info": {"version": version}}


# --- _extract_pinned_version ---

def test_extracts_pinned_version():
    dep = make_dep("requests", "==2.28.0")
    assert _extract_pinned_version(dep) == "2.28.0"


def test_returns_none_for_range_spec():
    dep = make_dep("requests", ">=2.0.0")
    assert _extract_pinned_version(dep) is None


def test_returns_none_for_no_spec():
    dep = make_dep("requests")
    assert _extract_pinned_version(dep) is None


# --- check_outdated ---

def test_no_issues_with_empty_list():
    result = check_outdated([], info_map={})
    assert not result.has_issues()


def test_no_issues_when_up_to_date():
    deps = [make_dep("requests", "==2.31.0")]
    info_map = {"requests": make_info("2.31.0")}
    result = check_outdated(deps, info_map=info_map)
    assert not result.has_issues()


def test_detects_outdated_package():
    deps = [make_dep("requests", "==2.28.0")]
    info_map = {"requests": make_info("2.31.0")}
    result = check_outdated(deps, info_map=info_map)
    assert result.has_issues()
    assert result.issues[0].package == "requests"
    assert result.issues[0].current_version == "2.28.0"
    assert result.issues[0].latest_version == "2.31.0"


def test_skips_unpinned_dependency():
    deps = [make_dep("flask", ">=2.0.0")]
    info_map = {"flask": make_info("3.0.0")}
    result = check_outdated(deps, info_map=info_map)
    assert not result.has_issues()


def test_skips_missing_pypi_info():
    deps = [make_dep("unknown-pkg", "==1.0.0")]
    result = check_outdated(deps, info_map={})
    assert not result.has_issues()


def test_multiple_deps_partial_outdated():
    deps = [
        make_dep("requests", "==2.28.0"),
        make_dep("flask", "==3.0.0"),
    ]
    info_map = {
        "requests": make_info("2.31.0"),
        "flask": make_info("3.0.0"),
    }
    result = check_outdated(deps, info_map=info_map)
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "requests"


def test_str_no_issues():
    result = OutdatedCheckResult(issues=[])
    assert "No outdated" in str(result)


def test_str_with_issues():
    result = OutdatedCheckResult(
        issues=[OutdatedIssue("requests", "2.28.0", "2.31.0")]
    )
    assert "requests" in str(result)
    assert "2.28.0" in str(result)
    assert "2.31.0" in str(result)


def test_issue_str():
    issue = OutdatedIssue("django", "3.2.0", "4.2.0")
    s = str(issue)
    assert "django" in s
    assert "3.2.0" in s
    assert "4.2.0" in s
