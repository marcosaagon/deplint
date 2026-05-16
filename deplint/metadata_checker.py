"""Check for missing or incomplete package metadata in requirements."""

from dataclasses import dataclass, field
from typing import List, Optional

from deplint.parser import Dependency


@dataclass
class MetadataIssue:
    package: str
    line_number: int
    missing_fields: List[str]

    def __str__(self) -> str:
        fields = ", ".join(self.missing_fields)
        return (
            f"Line {self.line_number}: '{self.package}' is missing metadata: {fields}"
        )


@dataclass
class MetadataCheckResult:
    issues: List[MetadataIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "No metadata issues found."
        lines = ["Metadata issues:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


# Fields expected to be present in PyPI package info
_REQUIRED_FIELDS = ["summary", "author", "license", "home_page"]


def check_metadata(
    deps: List[Dependency],
    package_info_map: Optional[dict] = None,
) -> MetadataCheckResult:
    """Check that each dependency has complete metadata on PyPI."""
    if package_info_map is None:
        package_info_map = {}

    issues: List[MetadataIssue] = []

    for dep in deps:
        key = dep.name.lower()
        info = package_info_map.get(key)
        if info is None:
            continue

        missing = [
            f for f in _REQUIRED_FIELDS
            if not info.get(f)
        ]
        if missing:
            issues.append(
                MetadataIssue(
                    package=dep.name,
                    line_number=dep.line_number,
                    missing_fields=missing,
                )
            )

    return MetadataCheckResult(issues=issues)
