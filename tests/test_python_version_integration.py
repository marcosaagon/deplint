"""Integration tests combining fetcher and checker for Python version feature."""
import pytest
from unittest.mock import patch
from deplint.python_version_fetcher import fetch_python_version_map
from deplint.python_version_checker import check_python_version_compatibility
from deplint.parser import Dependency


def make_dep(name: str, spec: str = "", line: int = 1) -> Dependency:
    return Dependency(name=name, version_spec=spec, extras=[], line_number=line)


def make_pypi_info(requires_python):
    return {"info": {"requires_python": requires_python, "classifiers": []}}


def test_full_pipeline_detects_incompatibility():
    deps = [make_dep("fastapi"), make_dep("oldlib")]
    fake_responses = {
        "fastapi": make_pypi_info(">=3.8"),
        "oldlib": make_pypi_info(">=3.6"),
    }

    def fake_fetch(name):
        return fake_responses.get(name)

    with patch("deplint.python_version_fetcher.fetch_package_info", side_effect=fake_fetch):
        version_map = fetch_python_version_map([d.name for d in deps])

    result = check_python_version_compatibility(
        deps, current_python="3.7", package_python_map=version_map
    )
    assert result.has_issues()
    names = [i.package for i in result.issues]
    assert "fastapi" in names
    assert "oldlib" not in names


def test_full_pipeline_no_issues_when_all_compatible():
    deps = [make_dep("mylib")]
    fake_responses = {"mylib": make_pypi_info(">=3.6")}

    def fake_fetch(name):
        return fake_responses.get(name)

    with patch("deplint.python_version_fetcher.fetch_package_info", side_effect=fake_fetch):
        version_map = fetch_python_version_map([d.name for d in deps])

    result = check_python_version_compatibility(
        deps, current_python="3.10", package_python_map=version_map
    )
    assert not result.has_issues()


def test_full_pipeline_handles_missing_pypi_info():
    deps = [make_dep("ghostpkg")]

    with patch("deplint.python_version_fetcher.fetch_package_info", return_value=None):
        version_map = fetch_python_version_map([d.name for d in deps])

    result = check_python_version_compatibility(
        deps, current_python="3.6", package_python_map=version_map
    )
    assert not result.has_issues()
