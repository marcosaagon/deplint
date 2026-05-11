"""Fetch package metadata (including license info) from PyPI."""
import urllib.request
import urllib.error
import json
from typing import Dict, List, Optional

from deplint.parser import Dependency

PYPI_URL = "https://pypi.org/pypi/{package}/json"


def fetch_package_info(package_name: str) -> Optional[dict]:
    """Fetch package metadata from PyPI. Returns None on failure."""
    url = PYPI_URL.format(package=package_name)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None


def extract_license(info: dict) -> Optional[str]:
    """Extract SPDX-style license identifier from PyPI package info dict."""
    raw = info.get("info", {}).get("license") or ""
    raw = raw.strip()
    if not raw or raw.lower() in ("unknown", "other", ""):
        # Fall back to classifiers
        classifiers = info.get("info", {}).get("classifiers", [])
        for classifier in classifiers:
            if classifier.startswith("License ::"):
                parts = classifier.split(" :: ")
                if len(parts) >= 3:
                    return parts[-1].strip()
        return None
    return raw


def fetch_licenses(dependencies: List[Dependency]) -> Dict[str, Optional[str]]:
    """Fetch license information for a list of dependencies.

    Returns a dict mapping package name -> license string (or None if unknown).
    """
    result: Dict[str, Optional[str]] = {}
    for dep in dependencies:
        info = fetch_package_info(dep.name)
        if info is None:
            result[dep.name] = None
        else:
            result[dep.name] = extract_license(info)
    return result
