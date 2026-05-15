"""Tests for deplint.extras_checker."""
import pytest
from deplint.extras_checker import check_extras, ExtrasCheckResult, ExtrasIssue


KNOWN = {
    "requests": ["security", "socks"],
    "celery": ["redis", "rabbitmq"],
    "uvicorn": ["standard"],
}


def make_dep(name, extras=None, line_number=None):
    class Dep:
        pass
    d = Dep()
    d.name = name
    d.extras = extras or []
    d.line_number = line_number
    return d


def test_no_issues_with_empty_list():
    result = check_extras([], KNOWN)
    assert not result.has_issues()


def test_no_issues_when_no_extras():
    deps = [make_dep("requests"), make_dep("celery")]
    result = check_extras(deps, KNOWN)
    assert not result.has_issues()


def test_no_issues_with_valid_extras():
    deps = [make_dep("requests", extras=["security"])]
    result = check_extras(deps, KNOWN)
    assert not result.has_issues()


def test_no_issues_for_unknown_package():
    """Packages not in registry are skipped — we can't validate them."""
    deps = [make_dep("somepackage", extras=["anything"])]
    result = check_extras(deps, KNOWN)
    assert not result.has_issues()


def test_detects_unknown_extra():
    deps = [make_dep("requests", extras=["nonexistent"], line_number=3)]
    result = check_extras(deps, KNOWN)
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "requests"
    assert "nonexistent" in result.issues[0].unknown


def test_detects_partial_unknown_extras():
    deps = [make_dep("celery", extras=["redis", "bogus"])]
    result = check_extras(deps, KNOWN)
    assert result.has_issues()
    issue = result.issues[0]
    assert "bogus" in issue.unknown
    assert "redis" not in issue.unknown


def test_extras_case_insensitive():
    deps = [make_dep("requests", extras=["Security"])]
    result = check_extras(deps, KNOWN)
    assert not result.has_issues()


def test_package_name_case_insensitive():
    deps = [make_dep("Requests", extras=["security"])]
    result = check_extras(deps, KNOWN)
    assert not result.has_issues()


def test_str_no_issues():
    result = ExtrasCheckResult(issues=[])
    assert "passed" in str(result)


def test_str_with_issues():
    issue = ExtrasIssue(package="requests", extras=["bad"], unknown=["bad"], line_number=5)
    result = ExtrasCheckResult(issues=[issue])
    text = str(result)
    assert "requests" in text
    assert "bad" in text


def test_issue_str_includes_line_number():
    issue = ExtrasIssue(package="celery", extras=["x"], unknown=["x"], line_number=12)
    assert "line 12" in str(issue)


def test_issue_str_no_line_number():
    issue = ExtrasIssue(package="celery", extras=["x"], unknown=["x"])
    assert "line" not in str(issue)
