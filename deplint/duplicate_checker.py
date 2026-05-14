"""Checker for duplicate and redundant dependency specifications."""

from dataclasses import dataclass, field
from typing import List
from deplint.parser import Dependency


@dataclass
class DuplicateIssue:
    package: str
    occurrences: List[int]  # line numbers
    message: str = ""

    def __str__(self) -> str:
        lines = ", ".join(str(n) for n in self.occurrences)
        return (
            f"{self.package}: duplicate entry found on lines [{lines}]. "
            f"{self.message}"
        )


@dataclass
class DuplicateCheckResult:
    issues: List[DuplicateIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.has_issues():
            return "No duplicate dependency issues found."
        lines = ["Duplicate dependency issues:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def check_duplicates(dependencies: List[Dependency]) -> DuplicateCheckResult:
    """Detect packages listed more than once in a requirements file."""
    seen: dict = {}

    for dep in dependencies:
        key = dep.name.lower()
        if key not in seen:
            seen[key] = []
        seen[key].append(dep)

    issues = []
    for key, deps in seen.items():
        if len(deps) > 1:
            line_numbers = [
                d.line_number for d in deps if d.line_number is not None
            ]
            specs = ", ".join(
                d.version_spec or "(no version)" for d in deps
            )
            issues.append(
                DuplicateIssue(
                    package=deps[0].name,
                    occurrences=line_numbers,
                    message=f"Specs: {specs}",
                )
            )

    return DuplicateCheckResult(issues=issues)
