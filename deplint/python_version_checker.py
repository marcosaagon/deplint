"""Checker for Python version compatibility issues in requirements."""
from dataclasses import dataclass, field
from typing import List, Optional
from deplint.parser import Dependency

PYTHON_VERSION_CLASSIFIERS = {
    "requests": ">=3.6",
    "django": ">=3.8",
    "flask": ">=3.8",
    "numpy": ">=3.9",
    "pandas": ">=3.9",
    "scipy": ">=3.9",
    "fastapi": ">=3.8",
    "pydantic": ">=3.8",
    "sqlalchemy": ">=3.7",
    "pytest": ">=3.8",
}


@dataclass
class PythonVersionIssue:
    package: str
    required_python: str
    line_number: Optional[int] = None

    def __str__(self) -> str:
        loc = f" (line {self.line_number})" if self.line_number else ""
        return (
            f"{self.package}{loc} requires Python {self.required_python}"
        )


@dataclass
class PythonVersionCheckResult:
    issues: List[PythonVersionIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.has_issues():
            return "Python version compatibility: OK"
        lines = ["Python version compatibility issues:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def check_python_version_compatibility(
    deps: List[Dependency],
    current_python: str = "3.7",
    package_python_map: Optional[dict] = None,
) -> PythonVersionCheckResult:
    """Check if packages are compatible with the given Python version."""
    if package_python_map is None:
        package_python_map = PYTHON_VERSION_CLASSIFIERS

    issues = []
    current = tuple(int(x) for x in current_python.split("."))

    for dep in deps:
        key = dep.name.lower()
        if key not in package_python_map:
            continue
        required_str = package_python_map[key].lstrip(">=")
        required = tuple(int(x) for x in required_str.split("."))
        if current < required:
            issues.append(
                PythonVersionIssue(
                    package=dep.name,
                    required_python=package_python_map[key],
                    line_number=dep.line_number,
                )
            )

    return PythonVersionCheckResult(issues=issues)
