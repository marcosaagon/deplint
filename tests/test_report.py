"""Tests for the AnalysisReport formatter."""

import pytest
from deplint.report import AnalysisReport
from deplint.version_checker import CheckResult as VersionCheckResult, VersionConflict
from deplint.license_checker import LicenseCheckResult, LicenseIssue
from deplint.deprecated_checker import DeprecationCheckResult, DeprecationIssue
from deplint.security_checker import SecurityCheckResult, SecurityIssue


def make_clean_report(source_file=None):
    return AnalysisReport(
        version_result=VersionCheckResult(conflicts=[]),
        license_result=LicenseCheckResult(issues=[]),
        deprecated_result=DeprecationCheckResult(issues=[]),
        security_result=SecurityCheckResult(issues=[]),
        source_file=source_file,
    )


def test_no_issues_report():
    report = make_clean_report()
    assert not report.has_any_issues()


def test_summary_no_issues():
    report = make_clean_report()
    summary = report.summary()
    assert "Total issues: 0" in summary


def test_summary_counts_issues():
    sec_issue = SecurityIssue("requests", "2.28.0", "CVE-2023-32681", "desc")
    report = AnalysisReport(
        version_result=VersionCheckResult(conflicts=[]),
        license_result=LicenseCheckResult(issues=[]),
        deprecated_result=DeprecationCheckResult(issues=[]),
        security_result=SecurityCheckResult(issues=[sec_issue]),
    )
    assert report.has_any_issues()
    assert "security=1" in report.summary()


def test_format_includes_source_file():
    report = make_clean_report(source_file="requirements.txt")
    output = report.format(verbose=True)
    assert "requirements.txt" in output


def test_format_verbose_shows_all_sections():
    report = make_clean_report()
    output = report.format(verbose=True)
    assert "Version Conflicts" in output
    assert "License Issues" in output
    assert "Deprecated Packages" in output
    assert "Security Vulnerabilities" in output


def test_format_non_verbose_hides_clean_sections():
    report = make_clean_report()
    output = report.format(verbose=False)
    assert "Version Conflicts" not in output
    assert "Security Vulnerabilities" not in output


def test_format_shows_section_when_issue_present():
    sec_issue = SecurityIssue("pillow", "9.0.0", "CVE-2022-45199", "DoS")
    report = AnalysisReport(
        version_result=VersionCheckResult(conflicts=[]),
        license_result=LicenseCheckResult(issues=[]),
        deprecated_result=DeprecationCheckResult(issues=[]),
        security_result=SecurityCheckResult(issues=[sec_issue]),
    )
    output = report.format(verbose=False)
    assert "Security Vulnerabilities" in output
    assert "CVE-2022-45199" in output


def test_format_always_shows_summary():
    report = make_clean_report()
    output = report.format()
    assert "Total issues:" in output
