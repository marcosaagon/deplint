"""Tests for deplint.typo_checker."""
import pytest
from deplint.typo_checker import check_typos, TypoIssue, TypoCheckResult


def make_dep(name: str, line_number: int = 1):
    """Minimal dependency stub."""
    class _Dep:
        def __init__(self, name, line_number):
            self.name = name
            self.line_number = line_number
    return _Dep(name, line_number)


def test_no_issues_with_empty_list():
    result = check_typos([])
    assert not result.has_issues()


def test_no_issues_with_valid_packages():
    deps = [make_dep("requests"), make_dep("django"), make_dep("numpy")]
    result = check_typos(deps)
    assert not result.has_issues()


def test_detects_simple_typo():
    deps = [make_dep("requets", line_number=3)]
    result = check_typos(deps)
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "requets"
    assert result.issues[0].likely_intended == "requests"
    assert result.issues[0].line_number == 3


def test_detects_django_typo():
    deps = [make_dep("Djano", line_number=5)]
    result = check_typos(deps)
    assert result.has_issues()
    assert result.issues[0].likely_intended == "django"


def test_case_insensitive_detection():
    deps = [make_dep("NUMPPY", line_number=2)]
    result = check_typos(deps)
    assert result.has_issues()
    assert result.issues[0].likely_intended == "numpy"


def test_hyphen_normalisation():
    # 'fast-ap' normalises to 'fastap' which is in the map
    deps = [make_dep("fast-ap", line_number=7)]
    result = check_typos(deps)
    assert result.has_issues()


def test_underscore_normalisation():
    deps = [make_dep("sql_alchmy", line_number=9)]
    result = check_typos(deps)
    assert result.has_issues()
    assert result.issues[0].likely_intended == "sqlalchemy"


def test_multiple_typos_detected():
    deps = [
        make_dep("requests", 1),
        make_dep("requets", 2),
        make_dep("flask", 3),
        make_dep("numpy", 4),
        make_dep("numppy", 5),
    ]
    result = check_typos(deps)
    assert result.has_issues()
    assert len(result.issues) == 3


def test_str_with_no_issues():
    result = TypoCheckResult(issues=[])
    assert "no issues" in str(result).lower()


def test_str_with_issues():
    issue = TypoIssue(package="requets", likely_intended="requests", line_number=1)
    result = TypoCheckResult(issues=[issue])
    output = str(result)
    assert "requets" in output
    assert "requests" in output


def test_issue_str_with_suggestion():
    issue = TypoIssue(package="flask", likely_intended="flask", line_number=10)
    text = str(issue)
    assert "flask" in text
    assert "flask" in text
    assert "10" in text


def test_issue_str_without_suggestion():
    issue = TypoIssue(package="somepkg", likely_intended=None, line_number=4)
    text = str(issue)
    assert "somepkg" in text
    assert "suspicious" in text.lower()
