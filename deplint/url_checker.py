"""Checker for dependencies specified via direct URLs instead of package names."""

from dataclasses import dataclass, field
from typing import List

from deplint.parser import Dependency

# Patterns that indicate a direct URL dependency
_URL_INDICATORS = ("http://", "https://", "git+", "git://", "svn+", "hg+", "file://")


@dataclass
class UrlIssue:
    package: str
    line_number: int
    url_fragment: str

    def __str__(self) -> str:
        return (
            f"Line {self.line_number}: '{self.package}' is pinned to a direct URL "
            f"({self.url_fragment!r}), which bypasses PyPI and may cause "
            "reproducibility issues."
        )


@dataclass
class UrlCheckResult:
    issues: List[UrlIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "URL check: no issues found."
        lines = ["URL check issues:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def _extract_url_fragment(version_spec: str) -> str:
    """Return the first URL-like token found in a version spec string."""
    for token in version_spec.split():
        if any(token.startswith(indicator) for indicator in _URL_INDICATORS):
            return token
    return version_spec[:60]


def check_url_dependencies(deps: List[Dependency]) -> UrlCheckResult:
    """Flag any dependency that uses a direct URL instead of a PyPI version spec."""
    issues: List[UrlIssue] = []
    for dep in deps:
        spec = dep.version_spec or ""
        if any(indicator in spec for indicator in _URL_INDICATORS):
            issues.append(
                UrlIssue(
                    package=dep.name,
                    line_number=dep.line_number,
                    url_fragment=_extract_url_fragment(spec),
                )
            )
    return UrlCheckResult(issues=issues)
