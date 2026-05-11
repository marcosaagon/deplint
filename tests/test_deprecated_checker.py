"""Tests for the deprecated package checker."""

import pytest

from deplint.deprecated_checker import (
    DeprecationCheckResult,
    DeprecationIssue,
    check_deprecations,
    check_known_deprecated,
    check_pypi_classifiers,
)
from deplint.parser import Dependency


def make_dep(name: str, version: str = ">=1.0") -> Dependency:
    return Dependency(name=name, version_spec=version, extras=[], raw_line=f"{name}{version}")


def test_no_issues_with_fresh_packages():
    deps = [make_dep("requests"), make_dep("flask"), make_dep("pytest")]
    result = check_deprecations(deps)
    # pytest itself is not in KNOWN_DEPRECATED as deprecated — only 'nose' is
    assert not result.has_issues()


def test_detects_known_deprecated_package():
    deps = [make_dep("nose")]
    result = check_deprecations(deps)
    assert result.has_issues()
    assert result.issues[0].package == "nose"
    assert result.issues[0].replacement == "pytest"
    assert result.issues[0].source == "known_list"


def test_deprecated_package_case_insensitive():
    deps = [make_dep("Nose"), make_dep("PEP8")]
    result = check_deprecations(deps)
    assert len(result.issues) == 2


def test_deprecated_no_replacement():
    deps = [make_dep("distribute")]
    result = check_deprecations(deps)
    assert result.has_issues()
    issue = result.issues[0]
    assert issue.replacement == "setuptools"


def test_pypi_classifier_deprecated():
    dep = make_dep("oldpkg")
    classifiers = ["Development Status :: 7 - Inactive"]
    issue = check_pypi_classifiers(dep, classifiers)
    assert issue is not None
    assert issue.source == "pypi_classifier"
    assert issue.package == "oldpkg"


def test_pypi_classifier_not_deprecated():
    dep = make_dep("activepkg")
    classifiers = ["Development Status :: 5 - Production/Stable"]
    issue = check_pypi_classifiers(dep, classifiers)
    assert issue is None


def test_classifiers_map_used_in_check():
    deps = [make_dep("mypkg")]
    classifiers_map = {"mypkg": ["Development Status :: 7 - Inactive"]}
    result = check_deprecations(deps, classifiers_map=classifiers_map)
    assert result.has_issues()
    assert result.issues[0].source == "pypi_classifier"


def test_known_deprecated_takes_priority_over_classifiers():
    """If a package is in the known list, classifiers are not checked."""
    deps = [make_dep("nose")]
    classifiers_map = {"nose": ["Development Status :: 7 - Inactive"]}
    result = check_deprecations(deps, classifiers_map=classifiers_map)
    assert len(result.issues) == 1
    assert result.issues[0].source == "known_list"


def test_empty_dependencies():
    result = check_deprecations([])
    assert not result.has_issues()


def test_str_with_replacement():
    issue = DeprecationIssue(package="nose", replacement="pytest", source="known_list")
    assert "nose" in str(issue)
    assert "pytest" in str(issue)
    assert "DEPRECATED" in str(issue)


def test_str_without_replacement():
    issue = DeprecationIssue(package="oldpkg", replacement=None, source="pypi_classifier")
    s = str(issue)
    assert "oldpkg" in s
    assert "DEPRECATED" in s


def test_result_str_no_issues():
    result = DeprecationCheckResult()
    assert "No deprecated" in str(result)


def test_result_str_with_issues():
    result = DeprecationCheckResult(
        issues=[DeprecationIssue(package="nose", replacement="pytest", source="known_list")]
    )
    assert "nose" in str(result)
