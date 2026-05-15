"""Tests for deplint.url_checker."""

import pytest
from deplint.url_checker import check_url_dependencies, UrlIssue, UrlCheckResult


class Dep:
    """Minimal stand-in for parser.Dependency."""

    def __init__(self, name: str, version_spec: str = "", line_number: int = 1):
        self.name = name
        self.version_spec = version_spec
        self.line_number = line_number


def make_dep(name, spec="", line=1):
    return Dep(name, spec, line)


# ---------------------------------------------------------------------------
# Basic cases
# ---------------------------------------------------------------------------

def test_no_issues_with_empty_list():
    result = check_url_dependencies([])
    assert not result.has_issues()


def test_no_issues_with_normal_version_specs():
    deps = [
        make_dep("requests", "==2.28.0"),
        make_dep("flask", ">=2.0,<3.0"),
        make_dep("numpy"),
    ]
    result = check_url_dependencies(deps)
    assert not result.has_issues()


def test_detects_https_url():
    deps = [make_dep("mylib", "https://example.com/mylib-1.0.tar.gz", line=3)]
    result = check_url_dependencies(deps)
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "mylib"
    assert result.issues[0].line_number == 3


def test_detects_git_plus_url():
    deps = [make_dep("myrepo", "git+https://github.com/user/myrepo.git@main", line=5)]
    result = check_url_dependencies(deps)
    assert result.has_issues()
    assert result.issues[0].package == "myrepo"


def test_detects_http_url():
    deps = [make_dep("oldlib", "http://internal.server/oldlib.whl", line=2)]
    result = check_url_dependencies(deps)
    assert result.has_issues()


def test_detects_file_url():
    deps = [make_dep("locallib", "file:///home/user/locallib", line=7)]
    result = check_url_dependencies(deps)
    assert result.has_issues()


def test_detects_multiple_url_deps():
    deps = [
        make_dep("safe", "==1.0.0"),
        make_dep("git_dep", "git+https://github.com/a/b.git", line=2),
        make_dep("also_safe", ">=0.1"),
        make_dep("url_dep", "https://files.example.com/pkg.tar.gz", line=4),
    ]
    result = check_url_dependencies(deps)
    assert result.has_issues()
    assert len(result.issues) == 2
    packages = {i.package for i in result.issues}
    assert packages == {"git_dep", "url_dep"}


# ---------------------------------------------------------------------------
# String representations
# ---------------------------------------------------------------------------

def test_issue_str_contains_package_name():
    issue = UrlIssue(package="mylib", line_number=4, url_fragment="https://x.com/f.tar.gz")
    assert "mylib" in str(issue)
    assert "4" in str(issue)


def test_result_str_no_issues():
    result = UrlCheckResult(issues=[])
    assert "no issues" in str(result).lower()


def test_result_str_with_issues():
    result = UrlCheckResult(
        issues=[UrlIssue(package="foo", line_number=1, url_fragment="git+https://...")]
    )
    assert "foo" in str(result)
