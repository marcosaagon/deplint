"""Tests for the license checker module."""
import pytest
from deplint.license_checker import (
    check_licenses,
    LicenseIssue,
    LicenseCheckResult,
    RESTRICTIVE_LICENSES,
    PERMISSIVE_LICENSES,
)


def test_no_issues_with_permissive_licenses():
    packages = {"requests": "MIT", "flask": "BSD-3-Clause", "click": "Apache-2.0"}
    result = check_licenses(packages)
    assert not result.has_issues


def test_detects_restrictive_license():
    packages = {"some-gpl-lib": "GPL-3.0"}
    result = check_licenses(packages)
    assert result.has_issues
    assert result.issues[0].package == "some-gpl-lib"
    assert result.issues[0].license_id == "GPL-3.0"


def test_detects_unknown_license():
    packages = {"mystery-pkg": None}
    result = check_licenses(packages)
    assert result.has_issues
    assert "could not be determined" in result.issues[0].reason


def test_allow_list_blocks_unlisted_license():
    packages = {"requests": "MIT", "other": "Apache-2.0"}
    result = check_licenses(packages, allow_list=["MIT"])
    assert result.has_issues
    issue_packages = [i.package for i in result.issues]
    assert "other" in issue_packages
    assert "requests" not in issue_packages


def test_allow_list_permits_listed_licenses():
    packages = {"requests": "MIT", "flask": "MIT"}
    result = check_licenses(packages, allow_list=["MIT"])
    assert not result.has_issues


def test_deny_list_blocks_specified_license():
    packages = {"safe-lib": "MIT", "bad-lib": "WTFPL"}
    result = check_licenses(packages, deny_list=["WTFPL"])
    assert result.has_issues
    assert result.issues[0].package == "bad-lib"


def test_deny_list_combined_with_restrictive():
    packages = {"gpl-pkg": "GPL-2.0", "custom-bad": "Proprietary"}
    result = check_licenses(packages, deny_list=["Proprietary"])
    assert len(result.issues) == 2


def test_empty_packages_no_issues():
    result = check_licenses({})
    assert not result.has_issues


def test_str_no_issues():
    result = check_licenses({"requests": "MIT"})
    assert "No license issues" in str(result)


def test_str_with_issues():
    packages = {"bad-lib": "GPL-3.0"}
    result = check_licenses(packages)
    output = str(result)
    assert "1 license issue" in output
    assert "bad-lib" in output


def test_license_issue_str_unknown():
    issue = LicenseIssue("pkg", None, "License could not be determined")
    assert "UNKNOWN" in str(issue)
    assert "pkg" in str(issue)


def test_license_issue_str_known():
    issue = LicenseIssue("pkg", "GPL-3.0", "License is restrictive or denied")
    assert "GPL-3.0" in str(issue)
