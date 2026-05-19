"""Tests for deplint.circular_fetcher."""
import pytest
from deplint.circular_fetcher import is_build_tool_from_classifiers, build_circular_map


def test_empty_classifiers_not_build_tool():
    assert not is_build_tool_from_classifiers([])


def test_unrelated_classifiers_not_build_tool():
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ]
    assert not is_build_tool_from_classifiers(classifiers)


def test_build_tools_classifier_detected():
    classifiers = ["Topic :: Software Development :: Build Tools"]
    assert is_build_tool_from_classifiers(classifiers)


def test_packaging_classifier_detected():
    classifiers = ["Topic :: System :: Archiving :: Packaging"]
    assert is_build_tool_from_classifiers(classifiers)


def test_case_insensitive_match():
    classifiers = ["topic :: software development :: build tools"]
    assert is_build_tool_from_classifiers(classifiers)


def test_build_circular_map_empty_input():
    result = build_circular_map({})
    assert result == {}


def test_build_circular_map_excludes_non_build_tools():
    classifiers_map = {
        "requests": ["License :: OSI Approved :: Apache Software License"],
        "flask": ["Framework :: Flask"],
    }
    result = build_circular_map(classifiers_map)
    assert result == {}


def test_build_circular_map_includes_build_tools():
    classifiers_map = {
        "flit": ["Topic :: Software Development :: Build Tools"],
        "requests": ["License :: OSI Approved :: MIT License"],
    }
    result = build_circular_map(classifiers_map)
    assert "flit" in result
    assert "requests" not in result


def test_build_circular_map_normalises_hyphens():
    classifiers_map = {
        "my-build-tool": ["Topic :: Software Development :: Build Tools"],
    }
    result = build_circular_map(classifiers_map)
    assert "my_build_tool" in result


def test_build_circular_map_warning_mentions_package():
    classifiers_map = {
        "hatch": ["Topic :: Software Development :: Build Tools"],
    }
    result = build_circular_map(classifiers_map)
    assert "hatch" in result["hatch"]
    assert "runtime" in result["hatch"]
