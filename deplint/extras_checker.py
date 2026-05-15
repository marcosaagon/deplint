"""Checker for unused or unknown package extras in requirements."""
from dataclasses import dataclass, field
from typing import List, Optional

KNOWN_EXTRAS: dict = {
    "requests": ["security", "socks"],
    "django": ["argon2", "bcrypt"],
    "celery": ["redis", "rabbitmq", "sqs", "mongodb", "memcache", "auth", "msgpack"],
    "uvicorn": ["standard"],
    "fastapi": ["all"],
    "sqlalchemy": ["asyncio", "mypy"],
    "pytest": ["testing"],
    "boto3": [],
}


@dataclass
class ExtrasIssue:
    package: str
    extras: List[str]
    unknown: List[str]
    line_number: Optional[int] = None

    def __str__(self) -> str:
        unknown_str = ", ".join(self.unknown)
        loc = f" (line {self.line_number})" if self.line_number else ""
        return (
            f"{self.package}{loc}: unknown extras [{unknown_str}] — "
            f"verify these extras exist for this package"
        )


@dataclass
class ExtrasCheckResult:
    issues: List[ExtrasIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.has_issues():
            return "Extras check passed: no unknown extras detected."
        lines = ["Extras issues found:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def check_extras(dependencies: list, known_extras: Optional[dict] = None) -> ExtrasCheckResult:
    """Check each dependency's extras against a known registry."""
    registry = known_extras if known_extras is not None else KNOWN_EXTRAS
    issues: List[ExtrasIssue] = []

    for dep in dependencies:
        if not dep.extras:
            continue
        pkg_lower = dep.name.lower()
        if pkg_lower not in registry:
            continue
        valid = [e.lower() for e in registry[pkg_lower]]
        unknown = [e for e in dep.extras if e.lower() not in valid]
        if unknown:
            issues.append(
                ExtrasIssue(
                    package=dep.name,
                    extras=dep.extras,
                    unknown=unknown,
                    line_number=dep.line_number,
                )
            )

    return ExtrasCheckResult(issues=issues)
