"""License checker for Python dependencies."""
from dataclasses import dataclass, field
from typing import List, Optional

# Licenses considered non-permissive or problematic for commercial use
RESTRICTIVE_LICENSES = {
    "GPL-2.0",
    "GPL-3.0",
    "AGPL-3.0",
    "LGPL-2.1",
    "LGPL-3.0",
    "EUPL-1.1",
    "EUPL-1.2",
    "OSL-3.0",
    "CDDL-1.0",
    "MPL-2.0",
}

PERMISSIVE_LICENSES = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Unlicense",
    "CC0-1.0",
    "WTFPL",
    "Zlib",
}


@dataclass
class LicenseIssue:
    package: str
    license_id: Optional[str]
    reason: str

    def __str__(self) -> str:
        license_str = self.license_id or "UNKNOWN"
        return f"{self.package} [{license_str}]: {self.reason}"


@dataclass
class LicenseCheckResult:
    issues: List[LicenseIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.has_issues:
            return "No license issues found."
        lines = [f"Found {len(self.issues)} license issue(s):"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def check_licenses(
    package_licenses: dict,
    allow_list: Optional[List[str]] = None,
    deny_list: Optional[List[str]] = None,
) -> LicenseCheckResult:
    """Check package licenses for issues.

    Args:
        package_licenses: Mapping of package name to SPDX license identifier (or None).
        allow_list: If provided, only these licenses are permitted.
        deny_list: If provided, these licenses are explicitly forbidden.
    """
    result = LicenseCheckResult()
    effective_deny = set(deny_list or []) | RESTRICTIVE_LICENSES

    for package, license_id in package_licenses.items():
        if license_id is None:
            result.issues.append(
                LicenseIssue(package, None, "License could not be determined")
            )
            continue

        normalized = license_id.strip()

        if allow_list and normalized not in allow_list:
            result.issues.append(
                LicenseIssue(
                    package,
                    normalized,
                    f"License not in allow list: {', '.join(sorted(allow_list))}",
                )
            )
        elif normalized in effective_deny:
            result.issues.append(
                LicenseIssue(package, normalized, "License is restrictive or denied")
            )

    return result
