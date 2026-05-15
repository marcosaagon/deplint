"""Tests for deplint.yanked_checker."""

import pytest
from deplint.parser import Dependency
from deplint.yanked_checker import YankedIssue, YankedCheckResult, check_yanked


def make_dep(name: str, version_spec: str = None, line: int = 1) -> Dependency:
    return Dependency(name=name, version_spec=version_spec, extras=[], line_number=line)


def make_release_files(yanked: bool, reason: str = None, count: int = 1):
    return [{"yanked": yanked, "yanked_reason": reason}] * count


# --- check_yanked ---

def test_no_issues_with_empty_list():
    result = check_yanked([], {})
    assert not result.has_issues()


def test_no_issues_when_no_package_info():
    dep = make_dep("requests", "==2.28.0")
    result = check_yanked([dep], {})
    assert not result.has_issues()


def test_no_issues_for_non_pinned_dep():
    dep = make_dep("requests", ">=2.0")
    info = {"releases": {"2.28.0": make_release_files(yanked=True)}}
    result = check_yanked([dep], {"requests": info})
    assert not result.has_issues()


def test_no_issues_for_dep_without_version():
    dep = make_dep("requests")
    info = {"releases": {"2.28.0": make_release_files(yanked=True)}}
    result = check_yanked([dep], {"requests": info})
    assert not result.has_issues()


def test_no_issues_for_non_yanked_version():
    dep = make_dep("requests", "==2.28.0")
    info = {"releases": {"2.28.0": make_release_files(yanked=False)}}
    result = check_yanked([dep], {"requests": info})
    assert not result.has_issues()


def test_detects_yanked_version():
    dep = make_dep("requests", "==2.28.0")
    info = {"releases": {"2.28.0": make_release_files(yanked=True)}}
    result = check_yanked([dep], {"requests": info})
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "requests"
    assert result.issues[0].version == "2.28.0"


def test_yanked_includes_reason():
    dep = make_dep("badpkg", "==1.0.0")
    info = {"releases": {"1.0.0": make_release_files(yanked=True, reason="Critical bug")}}
    result = check_yanked([dep], {"badpkg": info})
    assert result.issues[0].reason == "Critical bug"


def test_partial_yank_not_flagged():
    """If only some release files are yanked, the version is not fully yanked."""
    dep = make_dep("mypkg", "==3.0.0")
    files = [{"yanked": True, "yanked_reason": None}, {"yanked": False, "yanked_reason": None}]
    info = {"releases": {"3.0.0": files}}
    result = check_yanked([dep], {"mypkg": info})
    assert not result.has_issues()


def test_package_name_lookup_is_case_insensitive():
    dep = make_dep("Requests", "==2.28.0")
    info = {"releases": {"2.28.0": make_release_files(yanked=True)}}
    result = check_yanked([dep], {"requests": info})
    assert result.has_issues()


def test_str_no_issues():
    result = YankedCheckResult(issues=[])
    assert "No yanked" in str(result)


def test_str_with_issues():
    issue = YankedIssue(package="requests", version="2.28.0", reason="Security flaw")
    result = YankedCheckResult(issues=[issue])
    output = str(result)
    assert "requests" in output
    assert "2.28.0" in output
    assert "Security flaw" in output


def test_issue_str_without_reason():
    issue = YankedIssue(package="foo", version="0.1.0")
    assert str(issue) == "foo==0.1.0 has been yanked from PyPI"


def test_issue_str_with_reason():
    issue = YankedIssue(package="foo", version="0.1.0", reason="Bad release")
    assert "Bad release" in str(issue)
