"""Fetches package metadata from PyPI."""

import urllib.request
import urllib.error
import json
from typing import Any, Dict, List, Optional

PYPI_BASE_URL = "https://pypi.org/pypi/{package}/json"


def fetch_package_info(package_name: str) -> Optional[Dict[str, Any]]:
    """Fetch package metadata from PyPI. Returns None on failure."""
    url = PYPI_BASE_URL.format(package=package_name)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None


def extract_license(package_info: Dict[str, Any]) -> Optional[str]:
    """Extract the license string from PyPI package metadata."""
    info = package_info.get("info", {})
    license_field = info.get("license") or ""
    if license_field.strip():
        return license_field.strip()
    # Fall back to classifiers
    classifiers: List[str] = info.get("classifiers", [])
    for classifier in classifiers:
        if classifier.startswith("License ::"):
            parts = classifier.split(" :: ")
            if len(parts) >= 3:
                return parts[-1].strip()
    return None


def extract_classifiers(package_info: Dict[str, Any]) -> List[str]:
    """Extract all classifiers from PyPI package metadata."""
    info = package_info.get("info", {})
    return info.get("classifiers", [])


def fetch_licenses(package_names: List[str]) -> Dict[str, Optional[str]]:
    """Fetch licenses for multiple packages. Returns a dict of name -> license."""
    results: Dict[str, Optional[str]] = {}
    for name in package_names:
        info = fetch_package_info(name)
        if info:
            results[name] = extract_license(info)
        else:
            results[name] = None
    return results


def fetch_classifiers_map(package_names: List[str]) -> Dict[str, List[str]]:
    """Fetch classifiers for multiple packages. Returns a dict of name -> classifiers."""
    results: Dict[str, List[str]] = {}
    for name in package_names:
        info = fetch_package_info(name)
        if info:
            results[name.lower()] = extract_classifiers(info)
        else:
            results[name.lower()] = []
    return results
