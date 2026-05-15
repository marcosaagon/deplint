"""Checker for environment marker issues in dependency specifications."""

from dataclasses import dataclass, field
from typing import List

from deplint.parser import Dependency

KNOWN_MARKER_NAMES = {
    "os_name",
    "sys_platform",
    "platform_machine",
    "platform_python_implementation",
    "platform_release",
    "platform_system",
    "platform_version",
    "python_version",
    "python_full_version",
    "implementation_name",
    "implementation_version",
    "extra",
}


@dataclass
class MarkerIssue:
    package: str
    line_number: int
    marker: str
    reason: str

    def __str__(self) -> str:
        return (
            f"Line {self.line_number}: '{self.package}' has marker issue "
            f"in '{self.marker}': {self.reason}"
        )


@dataclass
class MarkerCheckResult:
    issues: List[MarkerIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.has_issues():
            return "No marker issues found."
        lines = ["Marker issues:"]
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)


def _extract_marker_name(marker: str) -> str:
    """Extract the environment marker variable name from a marker expression."""
    return marker.strip().split()[0] if marker.strip() else ""


def check_markers(deps: List[Dependency]) -> MarkerCheckResult:
    """Check dependencies for unknown or suspicious environment markers."""
    issues: List[MarkerIssue] = []

    for dep in deps:
        if not dep.marker:
            continue

        marker_name = _extract_marker_name(dep.marker)

        if not marker_name:
            issues.append(
                MarkerIssue(
                    package=dep.name,
                    line_number=dep.line_number,
                    marker=dep.marker,
                    reason="empty or blank marker expression",
                )
            )
            continue

        if marker_name not in KNOWN_MARKER_NAMES:
            issues.append(
                MarkerIssue(
                    package=dep.name,
                    line_number=dep.line_number,
                    marker=dep.marker,
                    reason=f"unknown marker name '{marker_name}'",
                )
            )

    return MarkerCheckResult(issues=issues)
