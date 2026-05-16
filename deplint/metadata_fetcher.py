"""Fetch and extract package metadata from PyPI responses."""

from typing import Dict, List, Optional

from deplint.fetcher import fetch_package_info


_METADATA_FIELDS = ["summary", "author", "license", "home_page"]


def extract_metadata(info: dict) -> dict:
    """Extract relevant metadata fields from a PyPI info dict."""
    pypi_info = info.get("info", {})
    return {
        field: pypi_info.get(field, "") or ""
        for field in _METADATA_FIELDS
    }


def fetch_metadata_map(package_names: List[str]) -> Dict[str, dict]:
    """Fetch metadata for a list of package names.

    Returns a dict mapping lowercase package name to its metadata dict.
    Packages that cannot be fetched are omitted.
    """
    result: Dict[str, dict] = {}
    for name in package_names:
        info = fetch_package_info(name)
        if info is not None:
            result[name.lower()] = extract_metadata(info)
    return result
