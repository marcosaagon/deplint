"""Tests for the security vulnerability checker."""

import pytest
from deplint.parser import Dependency
from deplint.security_checker import (
    SecurityIssue,
    SecurityCheckResult,
    check_security,
    _is_below,
)


def make_dep(name: str, version: str = None, specifier: str = None) -> Dependency:
    return Dependency(name=name, version=version, specifier=specifier, extras=[])


def test_no_issues_with_empty_list():
    result = check_security([])
    assert not result.has_issues()


def test_no_issues_with_safe_versions():
    deps = [
        make_dep("requests", "2.31.0"),
        make_dep("django", "4.2.0"),
    ]
    result = check_security(deps)
    assert not result.has_issues()


def test_detects_vulnerable_requests():
    deps = [make_dep("requests", "2.28.0")]
    result = check_security(deps)
    assert result.has_issues()
    assert any("CVE-2023-32681" in i.cve for i in result.issues)


def test_detects_vulnerable_django():
    deps = [make_dep("django", "2.2.10")]
    result = check_security(deps)
    assert result.has_issues()
    cves = {i.cve for i in result.issues}
    assert "CVE-2022-28346" in cves


def test_vulnerability_case_insensitive():
    deps = [make_dep("Django", "2.2.10")]
    result = check_security(deps)
    assert result.has_issues()


def test_no_issue_for_unknown_package():
    deps = [make_dep("someobscurelib", "0.1.0")]
    result = check_security(deps)
    assert not result.has_issues()


def test_unpinned_version_skipped():
    deps = [make_dep("requests", None)]
    result = check_security(deps)
    assert not result.has_issues()


def test_multiple_vulnerabilities_same_package():
    deps = [make_dep("django", "2.2.1")]
    result = check_security(deps)
    cves = {i.cve for i in result.issues}
    assert "CVE-2023-31047" in cves
    assert "CVE-2022-28346" in cves


def test_issue_str_format():
    issue = SecurityIssue(
        package="requests",
        version="2.28.0",
        cve="CVE-2023-32681",
        description="Proxy-Authorization header leak",
    )
    text = str(issue)
    assert "requests==2.28.0" in text
    assert "CVE-2023-32681" in text


def test_result_str_no_issues():
    result = SecurityCheckResult(issues=[])
    assert "No known" in str(result)


def test_result_str_with_issues():
    issue = SecurityIssue("pillow", "9.0.0", "CVE-2022-45199", "DoS via crafted image")
    result = SecurityCheckResult(issues=[issue])
    text = str(result)
    assert "1 security issue" in text
    assert "CVE-2022-45199" in text


def test_is_below_helper():
    assert _is_below("2.28.0", "2.31.0") is True
    assert _is_below("2.31.0", "2.31.0") is False
    assert _is_below("3.0.0", "2.31.0") is False
    assert _is_below(None, "2.31.0") is False
