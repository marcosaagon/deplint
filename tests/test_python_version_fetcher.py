"""Tests for the Python version fetcher utilities."""
import pytest
from unittest.mock import patch, MagicMock
from deplint.python_version_fetcher import (
    extract_python_requires,
    extract_python_classifiers,
    min_python_from_classifiers,
    fetch_python_version_map,
)


def make_info(requires_python=None, classifiers=None):
    return {
        "info": {
            "requires_python": requires_python,
            "classifiers": classifiers or [],
        }
    }


def test_extract_python_requires_present():
    info = make_info(requires_python=">=3.8")
    assert extract_python_requires(info) == ">=3.8"


def test_extract_python_requires_missing():
    info = make_info()
    assert extract_python_requires(info) is None


def test_extract_python_requires_empty_info():
    assert extract_python_requires({}) is None
    assert extract_python_requires(None) is None


def test_extract_python_classifiers_filters_correctly():
    classifiers = [
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ]
    info = make_info(classifiers=classifiers)
    result = extract_python_classifiers(info)
    assert len(result) == 2
    assert all("3." in c for c in result)


def test_extract_python_classifiers_empty():
    assert extract_python_classifiers({}) == []
    assert extract_python_classifiers(None) == []


def test_min_python_from_classifiers_finds_minimum():
    classifiers = [
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.8",
    ]
    result = min_python_from_classifiers(classifiers)
    assert result == ">=3.8"


def test_min_python_from_classifiers_empty():
    assert min_python_from_classifiers([]) is None


def test_min_python_from_classifiers_invalid_entries():
    classifiers = ["Programming Language :: Python :: badver"]
    assert min_python_from_classifiers(classifiers) is None


def test_fetch_python_version_map_uses_requires_python():
    info = make_info(requires_python=">=3.9")
    with patch("deplint.python_version_fetcher.fetch_package_info", return_value=info):
        result = fetch_python_version_map(["requests"])
    assert result == {"requests": ">=3.9"}


def test_fetch_python_version_map_falls_back_to_classifiers():
    classifiers = [
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ]
    info = make_info(classifiers=classifiers)
    with patch("deplint.python_version_fetcher.fetch_package_info", return_value=info):
        result = fetch_python_version_map(["somelib"])
    assert result == {"somelib": ">=3.8"}


def test_fetch_python_version_map_skips_no_info():
    with patch("deplint.python_version_fetcher.fetch_package_info", return_value=None):
        result = fetch_python_version_map(["unknownpkg"])
    assert result == {}
