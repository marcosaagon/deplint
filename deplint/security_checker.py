"""Security vulnerability checker for Python dependencies."""

from dataclasses import dataclass, field
from typing import List, Optional
from deplint.parser import Dependency

# Known vulnerable packages with affected version ranges and CVE references
KNOWN_VULNERABILITIES = {
    "django": [
        {"below": "3.2.19", "cve": "CVE-2023-31047", "description": "Potential bypass of validation"},
        {"below": "2.2.28", "cve": "CVE-2022-28346", "description": "SQL injection in QuerySet.annotate"},
    ],
    "pillow": [
        {"below": "9.3.0", "cve": "CVE-2022-45199", "description": "DoS via crafted image file"},
    ],
    "cryptography": [
        {"below": "41.0.0", "cve": "CVE-2023-38325", "description": "NULL pointer dereference in PKCS12"},
    ],
    "requests": [
        {"below": "2.31.0", "cve": "CVE-2023-32681", "description": "Proxy-Authorization header leak"},
    ],
    "pyyaml": [
        {"below": "6.0", "cve": "CVE-2022-1471", "description": "Arbitrary code execution via yaml.load"},
    ],
}


@dataclass
class SecurityIssue:
    package: str
    version: Optional[str]
    cve: str
    description: str

    def __str__(self) -> str:
        ver = self.version or "unpinned"
        return (
            f"{self.package}=={ver} is affected by {self.cve}: {self.description}"
        )


@dataclass
class SecurityCheckResult:
    issues: List[SecurityIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "No known security vulnerabilities found."
        lines = [f"Found {len(self.issues)} security issue(s):"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def _parse_version(version_str: Optional[str]):
    """Parse a version string into a tuple of ints for comparison."""
    if not version_str:
        return None
    try:
        return tuple(int(x) for x in version_str.split("."))
    except ValueError:
        return None


def _is_below(version: Optional[str], threshold: str) -> bool:
    """Return True if version is strictly below threshold."""
    v = _parse_version(version)
    t = _parse_version(threshold)
    if v is None or t is None:
        return False
    # Pad shorter tuple with zeros
    length = max(len(v), len(t))
    v = v + (0,) * (length - len(v))
    t = t + (0,) * (length - len(t))
    return v < t


def check_security(dependencies: List[Dependency]) -> SecurityCheckResult:
    """Check dependencies for known security vulnerabilities."""
    issues: List[SecurityIssue] = []
    for dep in dependencies:
        key = dep.name.lower()
        if key not in KNOWN_VULNERABILITIES:
            continue
        for vuln in KNOWN_VULNERABILITIES[key]:
            if _is_below(dep.version, vuln["below"]):
                issues.append(
                    SecurityIssue(
                        package=dep.name,
                        version=dep.version,
                        cve=vuln["cve"],
                        description=vuln["description"],
                    )
                )
    return SecurityCheckResult(issues=issues)
