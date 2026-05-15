"""Tests for deplint.hash_checker."""
import pytest
from deplint.hash_checker import check_hashes, HashCheckResult, HashIssue


class Dep:
    """Minimal stand-in for parser.Dependency."""

    def __init__(self, name, line_number=1, options=None):
        self.name = name
        self.line_number = line_number
        self.options = options or []


def make_dep(name, line_number=1, options=None):
    return Dep(name, line_number=line_number, options=options or [])


# ---------------------------------------------------------------------------
# Basic cases
# ---------------------------------------------------------------------------

def test_no_issues_with_empty_list():
    result = check_hashes([])
    assert not result.has_issues()


def test_no_issues_when_no_hashes_and_not_required():
    deps = [make_dep("requests", options=[])]
    result = check_hashes(deps, require_hashes=False)
    assert not result.has_issues()


def test_no_issues_with_valid_sha256():
    digest = "a" * 64
    deps = [make_dep("requests", options=[f"--hash=sha256:{digest}"])]
    result = check_hashes(deps)
    assert not result.has_issues()


def test_no_issues_with_valid_sha512():
    digest = "b" * 128
    deps = [make_dep("cryptography", options=[f"--hash=sha512:{digest}"])]
    result = check_hashes(deps)
    assert not result.has_issues()


# ---------------------------------------------------------------------------
# Unsupported algorithm
# ---------------------------------------------------------------------------

def test_detects_unsupported_algorithm():
    deps = [make_dep("requests", line_number=3, options=["--hash=md5:abc123"])]
    result = check_hashes(deps)
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].package == "requests"
    assert "md5" in result.issues[0].reason


def test_detects_sha1_as_unsupported():
    deps = [make_dep("flask", line_number=5, options=["--hash=sha1:deadbeef"])]
    result = check_hashes(deps)
    assert result.has_issues()
    assert "sha1" in result.issues[0].reason


# ---------------------------------------------------------------------------
# Empty digest
# ---------------------------------------------------------------------------

def test_detects_empty_digest():
    deps = [make_dep("django", line_number=7, options=["--hash=sha256:"])]
    result = check_hashes(deps)
    assert result.has_issues()
    assert "empty hash digest" in result.issues[0].reason


# ---------------------------------------------------------------------------
# require_hashes mode
# ---------------------------------------------------------------------------

def test_require_hashes_flags_missing_hash():
    deps = [make_dep("boto3", line_number=2, options=[])]
    result = check_hashes(deps, require_hashes=True)
    assert result.has_issues()
    assert "no hash specified" in result.issues[0].reason


def test_require_hashes_ok_when_hash_present():
    digest = "c" * 64
    deps = [make_dep("boto3", options=[f"--hash=sha256:{digest}"])]
    result = check_hashes(deps, require_hashes=True)
    assert not result.has_issues()


def test_require_hashes_reports_each_missing_dep():
    deps = [
        make_dep("requests", line_number=1),
        make_dep("flask", line_number=2),
    ]
    result = check_hashes(deps, require_hashes=True)
    assert len(result.issues) == 2


# ---------------------------------------------------------------------------
# __str__ helpers
# ---------------------------------------------------------------------------

def test_str_no_issues():
    result = HashCheckResult(issues=[])
    assert "OK" in str(result)


def test_str_with_issues():
    issue = HashIssue(package="requests", line_number=1, reason="bad algo 'md5'")
    result = HashCheckResult(issues=[issue])
    text = str(result)
    assert "requests" in text
    assert "md5" in text
