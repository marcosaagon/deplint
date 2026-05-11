"""Report formatter for deplint analysis results."""

from dataclasses import dataclass
from typing import Optional
from deplint.version_checker import CheckResult as VersionCheckResult
from deplint.license_checker import LicenseCheckResult
from deplint.deprecated_checker import DeprecationCheckResult
from deplint.security_checker import SecurityCheckResult

SECTION_SEP = "-" * 50


@dataclass
class AnalysisReport:
    version_result: VersionCheckResult
    license_result: LicenseCheckResult
    deprecated_result: DeprecationCheckResult
    security_result: SecurityCheckResult
    source_file: Optional[str] = None

    def has_any_issues(self) -> bool:
        return (
            self.version_result.has_conflicts()
            or self.license_result.has_issues()
            or self.deprecated_result.has_issues()
            or self.security_result.has_issues()
        )

    def summary(self) -> str:
        counts = [
            len(self.version_result.conflicts),
            len(self.license_result.issues),
            len(self.deprecated_result.issues),
            len(self.security_result.issues),
        ]
        total = sum(counts)
        return (
            f"Total issues: {total} "
            f"(version={counts[0]}, license={counts[1]}, "
            f"deprecated={counts[2]}, security={counts[3]})"
        )

    def format(self, verbose: bool = False) -> str:
        lines = []
        if self.source_file:
            lines.append(f"Analysis of: {self.source_file}")
            lines.append(SECTION_SEP)

        sections = [
            ("Version Conflicts", self.version_result, self.version_result.has_conflicts()),
            ("License Issues", self.license_result, self.license_result.has_issues()),
            ("Deprecated Packages", self.deprecated_result, self.deprecated_result.has_issues()),
            ("Security Vulnerabilities", self.security_result, self.security_result.has_issues()),
        ]

        for title, result, has_problem in sections:
            if has_problem or verbose:
                lines.append(f"[{title}]")
                lines.append(str(result))
                lines.append("")

        lines.append(SECTION_SEP)
        lines.append(self.summary())
        return "\n".join(lines)
