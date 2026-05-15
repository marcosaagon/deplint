"""Check for environment markers that may conflict with the target Python version."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from deplint.parser import Dependency

# Markers that specify a Python version constraint
PYTHON_ENV_MARKERS = {
    "python_version",
    "python_full_version",
    "implementation_version",
}


@dataclass
class EnvConflict:
    package: str
    line_number: int
    marker: str
    reason: str

    def __str__(self) -> str:
        return (
            f"Line {self.line_number}: '{self.package}' has environment marker "
            f"'{self.marker}' — {self.reason}"
        )


@dataclass
class EnvCheckResult:
    conflicts: List[EnvConflict] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.conflicts) > 0

    def __str__(self) -> str:
        if not self.has_issues():
            return "No environment marker conflicts detected."
        lines = ["Environment marker conflicts:"]
        for c in self.conflicts:
            lines.append(f"  - {c}")
        return "\n".join(lines)


def _parse_marker_key(marker: str) -> str:
    """Extract the left-hand side key from a simple marker expression."""
    for op in ("==", "!=", ">=", "<=", ">", "<", "~=", " in ", " not in "):
        if op in marker:
            return marker.split(op)[0].strip()
    return marker.strip()


def check_env_markers(
    deps: List[Dependency],
    target_python: str = "",
) -> EnvCheckResult:
    """Detect dependencies whose environment markers reference python_version
    in a potentially ambiguous or redundant way, or that use unknown marker keys.
    """
    result = EnvCheckResult()

    for dep in deps:
        if not dep.marker:
            continue

        marker_key = _parse_marker_key(dep.marker)

        if marker_key in PYTHON_ENV_MARKERS:
            # Flag markers that hard-code a single Python version with ==
            if "==" in dep.marker:
                result.conflicts.append(
                    EnvConflict(
                        package=dep.name,
                        line_number=dep.line_number,
                        marker=dep.marker,
                        reason="hard-coded '==' python version marker may break on other interpreters",
                    )
                )
        elif marker_key and not _is_known_marker(marker_key):
            result.conflicts.append(
                EnvConflict(
                    package=dep.name,
                    line_number=dep.line_number,
                    marker=dep.marker,
                    reason=f"unknown marker key '{marker_key}'",
                )
            )

    return result


_KNOWN_MARKERS = {
    "os_name", "sys_platform", "platform_machine", "platform_python_implementation",
    "platform_release", "platform_system", "platform_version",
    "python_version", "python_full_version", "implementation_name",
    "implementation_version", "extra",
}


def _is_known_marker(key: str) -> bool:
    return key in _KNOWN_MARKERS
