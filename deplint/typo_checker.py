"""Checker for common package name typos (potential typosquatting)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from deplint.parser import Dependency

# Well-known packages mapped to common typos / lookalikes
TYPO_MAP: dict[str, str] = {
    "requets": "requests",
    "reqeusts": "requests",
    "rquests": "requests",
    "djano": "django",
    "dajngo": "django",
    "djangoo": "django",
    "numppy": "numpy",
    "nmpy": "numpy",
    "pandes": "pandas",
    "pandass": "pandas",
    "scippy": "scipy",
    "matplotib": "matplotlib",
    "matplotlb": "matplotlib",
    "flask": "flask",
    "falsk": "flask",
    "flaskk": "flask",
    "fasapi": "fastapi",
    "fastap": "fastapi",
    "sqlalchmy": "sqlalchemy",
    "sqlalchmey": "sqlalchemy",
    "celrey": "celery",
    "celey": "celery",
    "pytets": "pytest",
    "pytset": "pytest",
    "pyyaml": None,  # legitimate, keep for reference
    "urlib3": "urllib3",
    "urllib": "urllib3",
    "boto": "boto3",
    "pliow": "pillow",
    "pilow": "pillow",
}


@dataclass
class TypoIssue:
    package: str
    likely_intended: str | None
    line_number: int

    def __str__(self) -> str:
        if self.likely_intended:
            return (
                f"Line {self.line_number}: '{self.package}' looks like a typo "
                f"— did you mean '{self.likely_intended}'?"
            )
        return f"Line {self.line_number}: '{self.package}' is a known suspicious package name."


@dataclass
class TypoCheckResult:
    issues: List[TypoIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "Typo check: no issues found."
        lines = ["Typo check issues:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def check_typos(deps: List[Dependency]) -> TypoCheckResult:
    """Check each dependency name against the known typo map."""
    issues: List[TypoIssue] = []
    for dep in deps:
        normalised = dep.name.lower().replace("-", "").replace("_", "")
        if normalised in TYPO_MAP:
            issues.append(
                TypoIssue(
                    package=dep.name,
                    likely_intended=TYPO_MAP[normalised],
                    line_number=dep.line_number,
                )
            )
    return TypoCheckResult(issues=issues)
