"""Checker for circular/self-referential dependency issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class CircularIssue:
    package: str
    line_number: int
    detail: str

    def __str__(self) -> str:
        return (
            f"Line {self.line_number}: '{self.package}' — {self.detail}"
        )


@dataclass
class CircularCheckResult:
    issues: List[CircularIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "CircularCheck: no issues found."
        lines = ["CircularCheck issues:"]
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)


# Packages that are known to be their own dependency (self-referential stubs)
_SELF_REFERENTIAL: dict[str, str] = {
    "setuptools": "setuptools bootstraps itself; pinning it can cause circular install loops",
    "pip": "pip manages itself; pinning pip as a runtime dependency is circular",
    "wheel": "wheel is a build backend that should not appear as a runtime dependency",
    "distribute": "distribute is an alias for setuptools and creates circular resolution",
}


def check_circular(deps: Sequence) -> CircularCheckResult:
    """Flag dependencies that are known to cause circular or self-referential issues."""
    result = CircularCheckResult()
    for dep in deps:
        normalised = dep.name.lower().replace("-", "_")
        if normalised in _SELF_REFERENTIAL:
            result.issues.append(
                CircularIssue(
                    package=dep.name,
                    line_number=getattr(dep, "line_number", 0),
                    detail=_SELF_REFERENTIAL[normalised],
                )
            )
    return result
