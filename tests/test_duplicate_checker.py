"""Tests for the duplicate dependency checker."""

import pytest
from deplint.parser import Dependency
from deplint.duplicate_checker import (
    check_duplicates,
    DuplicateCheckResult,
    DuplicateIssue,
)


def make_dep(name: str, version_spec: str = None, line_number: int = None) -> Dependency:
    return Dependency(name=name, version_spec=version_spec, line_number=line_number)


def test_no_issues_with_empty_list():
    result = check_duplicates([])
    assert not result.has_issues()


def test_no_issues_with_unique_packages():
    deps = [
        make_dep("requests", "==2.28.0", 1),
        make_dep("flask", "==2.2.0", 2),
        make_dep("numpy", ">=1.21", 3),
    ]
    result = check_duplicates(deps)
    assert not result.has_issues()
    assert len(result.issues) == 0


def test_detects_simple_duplicate():
    deps = [
        make_dep("requests", "==2.28.0", 1),
        make_dep("requests", "==2.27.0", 5),
    ]
    result = check_duplicates(deps)
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "requests"


def test_duplicate_records_line_numbers():
    deps = [
        make_dep("flask", "==2.0.0", 3),
        make_dep("flask", ">=1.0", 10),
    ]
    result = check_duplicates(deps)
    assert result.has_issues()
    issue = result.issues[0]
    assert 3 in issue.occurrences
    assert 10 in issue.occurrences


def test_duplicate_case_insensitive():
    deps = [
        make_dep("Django", "==4.0", 1),
        make_dep("django", "==3.2", 8),
    ]
    result = check_duplicates(deps)
    assert result.has_issues()
    assert len(result.issues) == 1


def test_triple_duplicate():
    deps = [
        make_dep("boto3", "==1.24.0", 1),
        make_dep("boto3", "==1.23.0", 4),
        make_dep("boto3", ">=1.20", 9),
    ]
    result = check_duplicates(deps)
    assert result.has_issues()
    assert len(result.issues[0].occurrences) == 3


def test_str_no_issues():
    result = DuplicateCheckResult(issues=[])
    assert "No duplicate" in str(result)


def test_str_with_issues():
    issue = DuplicateIssue(package="requests", occurrences=[1, 5], message="Specs: ==2.28.0, ==2.27.0")
    result = DuplicateCheckResult(issues=[issue])
    output = str(result)
    assert "requests" in output
    assert "Duplicate" in output


def test_issue_str_includes_lines():
    issue = DuplicateIssue(package="flask", occurrences=[2, 7], message="Specs: ==2.0.0, >=1.0")
    text = str(issue)
    assert "2" in text
    assert "7" in text
    assert "flask" in text


def test_multiple_different_duplicates():
    deps = [
        make_dep("requests", "==2.28.0", 1),
        make_dep("flask", "==2.0.0", 2),
        make_dep("requests", "==2.27.0", 5),
        make_dep("flask", ">=1.0", 8),
    ]
    result = check_duplicates(deps)
    assert result.has_issues()
    assert len(result.issues) == 2
    packages = {i.package.lower() for i in result.issues}
    assert "requests" in packages
    assert "flask" in packages
