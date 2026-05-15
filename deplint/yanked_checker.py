"""Checker for yanked package versions on PyPI."""

from dataclasses import dataclass, field
from typing import List, Optional

from deplint.parser import Dependency


@dataclass
class YankedIssue:
    package: str
    version: str
    reason: Optional[str] = None

    def __str__(self) -> str:
        msg = f"{self.package}=={self.version} has been yanked from PyPI"
        if self.reason:
            msg += f": {self.reason}"
        return msg


@dataclass
class YankedCheckResult:
    issues: List[YankedIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "No yanked packages detected."
        lines = ["Yanked packages detected:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def _extract_pinned_version(dep: Dependency) -> Optional[str]:
    """Return the pinned version string if the dep uses ==, else None."""
    if dep.version_spec and dep.version_spec.startswith("=="):
        return dep.version_spec[2:].strip()
    return None


def check_yanked(deps: List[Dependency], package_info_map: dict) -> YankedCheckResult:
    """Check whether any pinned dependency versions have been yanked on PyPI.

    Args:
        deps: List of Dependency objects to inspect.
        package_info_map: Mapping of package name (lowercase) to PyPI JSON info
                          dict (the 'releases' section expected).

    Returns:
        YankedCheckResult with any detected yanked versions.
    """
    issues: List[YankedIssue] = []

    for dep in deps:
        version = _extract_pinned_version(dep)
        if version is None:
            continue

        info = package_info_map.get(dep.name.lower())
        if info is None:
            continue

        releases = info.get("releases", {})
        files = releases.get(version, [])

        if not files:
            continue

        # A version is considered yanked if ALL its release files are yanked
        yanked_files = [f for f in files if f.get("yanked", False)]
        if yanked_files and len(yanked_files) == len(files):
            reason = yanked_files[0].get("yanked_reason") or None
            issues.append(YankedIssue(package=dep.name, version=version, reason=reason))

    return YankedCheckResult(issues=issues)
