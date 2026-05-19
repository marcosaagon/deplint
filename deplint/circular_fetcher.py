"""Utilities to build an extended circular-dependency map from PyPI metadata.

The static map in circular_checker covers well-known cases.  This module
allows callers to augment it at runtime by inspecting PyPI classifiers for
packages that declare themselves as 'build system' or 'framework' tools that
should not appear as runtime requirements.
"""
from __future__ import annotations

from typing import Dict, List

# Classifier fragments that indicate a package is a build/packaging tool
_BUILD_CLASSIFIER_FRAGMENTS: List[str] = [
    "Topic :: Software Development :: Build Tools",
    "Topic :: System :: Archiving :: Packaging",
]


def is_build_tool_from_classifiers(classifiers: List[str]) -> bool:
    """Return True if any classifier marks the package as a build tool."""
    for clf in classifiers:
        for fragment in _BUILD_CLASSIFIER_FRAGMENTS:
            if fragment.lower() in clf.lower():
                return True
    return False


def build_circular_map(classifiers_map: Dict[str, List[str]]) -> Dict[str, str]:
    """Return a mapping of package_name -> warning_detail for build-tool packages.

    Args:
        classifiers_map: {package_name: [classifier, ...]} as returned by
                         ``deplint.fetcher.fetch_classifiers_map``.

    Returns:
        Dict mapping lower-cased package names to a human-readable warning.
    """
    result: Dict[str, str] = {}
    for name, classifiers in classifiers_map.items():
        if is_build_tool_from_classifiers(classifiers):
            result[name.lower().replace("-", "_")] = (
                f"'{name}' is classified as a build/packaging tool and should "
                "not appear as a runtime dependency."
            )
    return result
