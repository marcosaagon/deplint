"""Checker for outdated package versions against PyPI."""
from dataclasses import dataclass, field
from typing import List, Optional
from packaging.version import Version, InvalidVersion
from deplint.parser import Dependency
from deplint.fetcher import fetch_package_info


@dataclass
class OutdatedIssue:
    package: str
    current_version: str
    latest_version: str
    message: str = ""

    def __str__(self) -> str:
        msg = self.message or (
            f"{self.package} is outdated: "
            f"current={self.current_version}, latest={self.latest_version}"
        )
        return msg


@dataclass
class OutdatedCheckResult:
    issues: List[OutdatedIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "No outdated packages found."
        lines = ["Outdated packages:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def _extract_pinned_version(dep: Dependency) -> Optional[str]:
    """Return pinned version string if dependency uses == specifier."""
    for spec in dep.version_specs:
        if spec.startswith("=="):
            return spec[2:].strip()
    return None


def _parse_version_safe(version_str: str) -> Optional[Version]:
    """Parse a version string, returning None if it is invalid."""
    try:
        return Version(version_str)
    except InvalidVersion:
        return None


def check_outdated(
    deps: List[Dependency],
    info_map: Optional[dict] = None,
) -> OutdatedCheckResult:
    """Check each pinned dependency against the latest version on PyPI.

    Args:
        deps: list of Dependency objects to check.
        info_map: optional dict mapping package name -> PyPI info dict
                  (used for testing without real HTTP calls).
    """
    issues: List[OutdatedIssue] = []

    for dep in deps:
        pinned = _extract_pinned_version(dep)
        if pinned is None:
            continue

        if info_map is not None:
            info = info_map.get(dep.name.lower())
        else:
            info = fetch_package_info(dep.name)

        if not info:
            continue

        latest_str = info.get("info", {}).get("version", "")
        if not latest_str:
            continue

        current = _parse_version_safe(pinned)
        latest = _parse_version_safe(latest_str)

        if current is None or latest is None:
            continue

        if current < latest:
            issues.append(
                OutdatedIssue(
                    package=dep.name,
                    current_version=pinned,
                    latest_version=latest_str,
                )
            )

    return OutdatedCheckResult(issues=issues)
