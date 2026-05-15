"""Fetch Python version requirements from PyPI classifiers."""
from typing import Dict, List, Optional
from deplint.fetcher import fetch_package_info


def extract_python_requires(info: dict) -> Optional[str]:
    """Extract requires_python field from PyPI package info."""
    if not info:
        return None
    return info.get("info", {}).get("requires_python") or None


def extract_python_classifiers(info: dict) -> List[str]:
    """Extract Python version classifiers from PyPI package info."""
    if not info:
        return []
    classifiers = info.get("info", {}).get("classifiers", []) or []
    return [
        c for c in classifiers
        if c.startswith("Programming Language :: Python :: 3.")
    ]


def min_python_from_classifiers(classifiers: List[str]) -> Optional[str]:
    """Derive the minimum Python 3.x version from classifier strings."""
    versions = []
    for c in classifiers:
        parts = c.split(" :: ")
        if len(parts) >= 3:
            ver = parts[-1]
            try:
                major, minor = ver.split(".")
                versions.append((int(major), int(minor)))
            except ValueError:
                continue
    if not versions:
        return None
    major, minor = min(versions)
    return f">={major}.{minor}"


def fetch_python_version_map(package_names: List[str]) -> Dict[str, str]:
    """Fetch minimum Python version requirements for a list of packages."""
    result = {}
    for name in package_names:
        info = fetch_package_info(name)
        if not info:
            continue
        requires = extract_python_requires(info)
        if requires:
            result[name.lower()] = requires
            continue
        classifiers = extract_python_classifiers(info)
        derived = min_python_from_classifiers(classifiers)
        if derived:
            result[name.lower()] = derived
    return result
