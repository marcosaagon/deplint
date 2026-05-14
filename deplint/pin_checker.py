"""Checker for unpinned or loosely pinned dependencies."""

from dataclasses import dataclass, field
from typing import List
from deplint.parser import Dependency


@dataclass
class PinIssue:
    package: str
    spec: str
    reason: str

    def __str__(self) -> str:
        return f"{self.package} ({self.spec or 'no version'}): {self.reason}"


@dataclass
class PinCheckResult:
    issues: List[PinIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "No pin issues found."
        lines = ["Pin issues detected:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def check_pins(deps: List[Dependency]) -> PinCheckResult:
    """Check each dependency for missing or loose version pins."""
    issues: List[PinIssue] = []

    for dep in deps:
        spec = dep.version_spec or ""

        if not spec:
            issues.append(PinIssue(
                package=dep.name,
                spec=spec,
                reason="No version specified; pin to a specific version for reproducibility",
            ))
        elif spec.startswith(">") and not spec.startswith(">="):
            issues.append(PinIssue(
                package=dep.name,
                spec=spec,
                reason="Strictly greater-than constraint may pull in untested versions",
            ))
        elif spec.startswith("~="):
            # Compatible release is acceptable but worth noting
            pass
        elif spec.startswith("=="):
            # Exact pin — ideal
            pass
        elif spec.startswith(">=") and "," not in spec:
            issues.append(PinIssue(
                package=dep.name,
                spec=spec,
                reason="Open upper bound; consider adding an upper bound or pinning exactly",
            ))

    return PinCheckResult(issues=issues)
