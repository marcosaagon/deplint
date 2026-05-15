"""Tests for deplint.namespace_checker."""

import pytest
from deplint.namespace_checker import check_namespaces, NamespaceIssue, NamespaceCheckResult


def make_dep(name, line_number=1):
    """Create a minimal Dependency-like object for testing."""
    class Dep:
        def __init__(self, name, line_number):
            self.name = name
            self.line_number = line_number
    return Dep(name, line_number)


def test_no_issues_with_empty_list():
    result = check_namespaces([])
    assert not result.has_issues()


def test_no_issues_with_unrelated_packages():
    deps = [make_dep("requests"), make_dep("flask"), make_dep("pytest")]
    result = check_namespaces(deps)
    assert not result.has_issues()


def test_no_issues_with_single_namespace_package():
    # Only one google package — no conflict
    deps = [make_dep("google-auth", line_number=3)]
    result = check_namespaces(deps)
    assert not result.has_issues()


def test_detects_google_namespace_conflict():
    deps = [
        make_dep("google-cloud-storage", line_number=1),
        make_dep("google-auth", line_number=2),
    ]
    result = check_namespaces(deps)
    assert result.has_issues()
    assert len(result.issues) == 2
    namespaces = {i.namespace for i in result.issues}
    assert namespaces == {"google"}


def test_detects_azure_namespace_conflict():
    deps = [
        make_dep("azure-storage-blob", line_number=5),
        make_dep("azure-identity", line_number=6),
    ]
    result = check_namespaces(deps)
    assert result.has_issues()
    packages = {i.package for i in result.issues}
    assert "azure-storage-blob" in packages
    assert "azure-identity" in packages


def test_conflict_records_line_number():
    deps = [
        make_dep("google-cloud-storage", line_number=10),
        make_dep("google-auth", line_number=20),
    ]
    result = check_namespaces(deps)
    line_numbers = {i.line_number for i in result.issues}
    assert 10 in line_numbers
    assert 20 in line_numbers


def test_namespace_conflict_case_insensitive():
    deps = [
        make_dep("Google-Cloud-Storage", line_number=1),
        make_dep("google-auth", line_number=2),
    ]
    result = check_namespaces(deps)
    assert result.has_issues()


def test_str_no_issues():
    result = NamespaceCheckResult()
    assert "no issues" in str(result)


def test_str_with_issues():
    issue = NamespaceIssue(
        package="google-auth",
        namespace="google",
        conflicting_packages=["google-cloud-storage"],
        line_number=4,
    )
    result = NamespaceCheckResult(issues=[issue])
    output = str(result)
    assert "google-auth" in output
    assert "google" in output


def test_issue_str_format():
    issue = NamespaceIssue(
        package="boto3",
        namespace="boto",
        conflicting_packages=["boto"],
        line_number=7,
    )
    text = str(issue)
    assert "Line 7" in text
    assert "boto3" in text
    assert "boto" in text
