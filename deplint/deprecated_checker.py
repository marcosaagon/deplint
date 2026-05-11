"""Checker for deprecated packages using PyPI classifiers and known deprecations."""

from dataclasses import dataclass, field
from typing import List, Optional

from deplint.parser import Dependency

# Well-known deprecated packages and their recommended replacements
KNOWN_DEPRECATED: dict = {
    "distribute": "setuptools",
    "pep8": "pycodestyle",
    "flake8-pep8": "flake8",
    "nose": "pytest",
    "mock": "unittest.mock (stdlib)",
    "futures": "concurrent.futures (stdlib)",
    "typing": "typing (stdlib, Python 3.5+)",
    "python-dateutil": None,  # not deprecated, example placeholder
    "py2-ipaddress": "ipaddress (stdlib)",
    "wsgiref": "wsgiref (stdlib)",
    "django-jsonfield": "django.db.models.JSONField (Django 3.1+)",
}


@dataclass
class DeprecationIssue:
    package: str
    replacement: Optional[str]
    source: str  # 'known_list' or 'pypi_classifier'

    def __str__(self) -> str:
        msg = f"[DEPRECATED] '{self.package}' is deprecated"
        if self.replacement:
            msg += f" — use '{self.replacement}' instead"
        msg += f" (source: {self.source})"
        return msg


@dataclass
class DeprecationCheckResult:
    issues: List[DeprecationIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "No deprecated packages found."
        lines = [str(issue) for issue in self.issues]
        return "\n".join(lines)


def check_known_deprecated(dep: Dependency) -> Optional[DeprecationIssue]:
    """Check if a dependency is in the known deprecated packages list."""
    name_lower = dep.name.lower()
    for deprecated_name, replacement in KNOWN_DEPRECATED.items():
        if name_lower == deprecated_name.lower():
            return DeprecationIssue(
                package=dep.name,
                replacement=replacement,
                source="known_list",
            )
    return None


def check_pypi_classifiers(dep: Dependency, classifiers: List[str]) -> Optional[DeprecationIssue]:
    """Check PyPI classifiers for deprecation indicators."""
    deprecation_keywords = ["inactive", "deprecated", "obsolete", "abandoned"]
    for classifier in classifiers:
        lower = classifier.lower()
        if any(kw in lower for kw in deprecation_keywords):
            return DeprecationIssue(
                package=dep.name,
                replacement=None,
                source="pypi_classifier",
            )
    return None


def check_deprecations(
    dependencies: List[Dependency],
    classifiers_map: Optional[dict] = None,
) -> DeprecationCheckResult:
    """Run deprecation checks on a list of dependencies."""
    result = DeprecationCheckResult()
    classifiers_map = classifiers_map or {}

    for dep in dependencies:
        issue = check_known_deprecated(dep)
        if issue:
            result.issues.append(issue)
            continue

        classifiers = classifiers_map.get(dep.name.lower(), [])
        if classifiers:
            issue = check_pypi_classifiers(dep, classifiers)
            if issue:
                result.issues.append(issue)

    return result
