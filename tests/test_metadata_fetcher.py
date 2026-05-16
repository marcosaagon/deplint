"""Tests for deplint.metadata_fetcher."""

from unittest.mock import patch
import pytest

from deplint.metadata_fetcher import extract_metadata, fetch_metadata_map


def make_pypi_response(summary="", author="", license_="", home_page=""):
    return {
        "info": {
            "summary": summary,
            "author": author,
            "license": license_,
            "home_page": home_page,
        }
    }


def test_extract_metadata_full():
    raw = make_pypi_response(
        summary="Desc", author="Bob", license_="MIT", home_page="https://x.com"
    )
    result = extract_metadata(raw)
    assert result["summary"] == "Desc"
    assert result["author"] == "Bob"
    assert result["license"] == "MIT"
    assert result["home_page"] == "https://x.com"


def test_extract_metadata_missing_fields():
    result = extract_metadata({"info": {}})
    assert result["summary"] == ""
    assert result["author"] == ""


def test_extract_metadata_none_values_become_empty():
    raw = {"info": {"summary": None, "author": None, "license": None, "home_page": None}}
    result = extract_metadata(raw)
    for v in result.values():
        assert v == ""


def test_extract_metadata_empty_info_key():
    result = extract_metadata({})
    assert all(v == "" for v in result.values())


def test_fetch_metadata_map_returns_results():
    fake_info = make_pypi_response(summary="S", author="A", license_="MIT", home_page="H")
    with patch("deplint.metadata_fetcher.fetch_package_info", return_value=fake_info):
        result = fetch_metadata_map(["requests"])
    assert "requests" in result
    assert result["requests"]["summary"] == "S"


def test_fetch_metadata_map_skips_failed_fetches():
    with patch("deplint.metadata_fetcher.fetch_package_info", return_value=None):
        result = fetch_metadata_map(["nonexistent"])
    assert result == {}


def test_fetch_metadata_map_lowercases_keys():
    fake_info = make_pypi_response(summary="S", author="A", license_="MIT", home_page="H")
    with patch("deplint.metadata_fetcher.fetch_package_info", return_value=fake_info):
        result = fetch_metadata_map(["Django"])
    assert "django" in result
