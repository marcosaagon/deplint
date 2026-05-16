"""Integration tests for metadata checking pipeline."""

from unittest.mock import patch
from deplint.parser import parse_requirements
from deplint.metadata_fetcher import fetch_metadata_map
from deplint.metadata_checker import check_metadata


REQUIREMENTS = """requests==2.28.0
flask==2.3.0
"""


def _make_info(summary="", author="", license_="", home_page=""):
    return {
        "info": {
            "summary": summary,
            "author": author,
            "license": license_,
            "home_page": home_page,
        }
    }


def test_full_pipeline_no_issues_when_metadata_complete():
    deps = parse_requirements(REQUIREMENTS)
    full = _make_info(summary="S", author="A", license_="MIT", home_page="H")
    with patch("deplint.metadata_fetcher.fetch_package_info", return_value=full):
        info_map = fetch_metadata_map([d.name for d in deps])
    result = check_metadata(deps, info_map)
    assert not result.has_issues()


def test_full_pipeline_detects_missing_metadata():
    deps = parse_requirements(REQUIREMENTS)
    incomplete = _make_info(summary="S", author="", license_="", home_page="")
    with patch("deplint.metadata_fetcher.fetch_package_info", return_value=incomplete):
        info_map = fetch_metadata_map([d.name for d in deps])
    result = check_metadata(deps, info_map)
    assert result.has_issues()
    packages = [i.package for i in result.issues]
    assert "requests" in packages
    assert "flask" in packages


def test_full_pipeline_partial_info_available():
    deps = parse_requirements(REQUIREMENTS)
    full = _make_info(summary="S", author="A", license_="MIT", home_page="H")
    incomplete = _make_info(summary="", author="", license_="", home_page="")

    call_count = {"n": 0}

    def fake_fetch(name):
        call_count["n"] += 1
        if name.lower() == "requests":
            return full
        return incomplete

    with patch("deplint.metadata_fetcher.fetch_package_info", side_effect=fake_fetch):
        info_map = fetch_metadata_map([d.name for d in deps])

    result = check_metadata(deps, info_map)
    assert result.has_issues()
    packages = [i.package for i in result.issues]
    assert "requests" not in packages
    assert "flask" in packages
