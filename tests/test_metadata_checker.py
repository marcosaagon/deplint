"""Tests for deplint.metadata_checker."""

import pytest
from deplint.metadata_checker import (
    MetadataIssue,
    MetadataCheckResult,
    check_metadata,
)


def make_dep(name, line_number=1):
    class _Dep:
        pass
    d = _Dep()
    d.name = name
    d.line_number = line_number
    return d


FULL_INFO = {
    "summary": "A great package",
    "author": "Alice",
    "license": "MIT",
    "home_page": "https://example.com",
}

MISSING_AUTHOR = {
    "summary": "A great package",
    "author": "",
    "license": "MIT",
    "home_page": "https://example.com",
}

MISSING_MANY = {
    "summary": "",
    "author": "",
    "license": "",
    "home_page": "",
}


def test_no_issues_with_empty_list():
    result = check_metadata([], {})
    assert not result.has_issues()


def test_no_issues_when_no_info_available():
    dep = make_dep("requests")
    result = check_metadata([dep], {})
    assert not result.has_issues()


def test_no_issues_with_full_metadata():
    dep = make_dep("requests")
    result = check_metadata([dep], {"requests": FULL_INFO})
    assert not result.has_issues()


def test_detects_missing_author():
    dep = make_dep("requests", line_number=3)
    result = check_metadata([dep], {"requests": MISSING_AUTHOR})
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "requests"
    assert "author" in result.issues[0].missing_fields
    assert result.issues[0].line_number == 3


def test_detects_multiple_missing_fields():
    dep = make_dep("mypackage", line_number=5)
    result = check_metadata([dep], {"mypackage": MISSING_MANY})
    assert result.has_issues()
    missing = result.issues[0].missing_fields
    assert "summary" in missing
    assert "author" in missing
    assert "license" in missing
    assert "home_page" in missing


def test_lookup_is_case_insensitive():
    dep = make_dep("Requests")
    result = check_metadata([dep], {"requests": MISSING_AUTHOR})
    assert result.has_issues()


def test_str_no_issues():
    result = MetadataCheckResult(issues=[])
    assert "No metadata issues" in str(result)


def test_str_with_issues():
    issue = MetadataIssue(package="foo", line_number=2, missing_fields=["author"])
    result = MetadataCheckResult(issues=[issue])
    text = str(result)
    assert "foo" in text
    assert "author" in text


def test_issue_str_format():
    issue = MetadataIssue(package="bar", line_number=7, missing_fields=["license", "home_page"])
    text = str(issue)
    assert "Line 7" in text
    assert "bar" in text
    assert "license" in text
    assert "home_page" in text
