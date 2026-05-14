"""Aggregate report combining all checker results."""

from dataclasses import dataclass, field
from typing import Optional
from deplint.version_checker import CheckResult as VersionCheckResult
from deplint.deprecated_checker import DeprecationCheckResult
from deplint.security_checker import SecurityCheckResult
from deplint.pin_checker import PinCheckResult


@dataclass
class AnalysisReport:
    source_file: str
    version_result: VersionCheckResult
    deprecated_result: DeprecationCheckResult
    security_result: SecurityCheckResult
    pin_result: PinCheckResult

    def has_any_issues(self) -> bool:
        return (
            self.version_result.has_conflicts()
            or self.deprecated_result.has_issues()
            or self.security_result.has_issues()
            or self.pin_result.has_issues()
        )

    def summary(self) -> str:
        parts = []
        vc = len(self.version_result.conflicts)
        dc = len(self.deprecated_result.issues)
        sc = len(self.security_result.issues)
        pc = len(self.pin_result.issues)
        if vc:
            parts.append(f"{vc} version conflict(s)")
        if dc:
            parts.append(f"{dc} deprecated package(s)")
        if sc:
            parts.append(f"{sc} security issue(s)")
        if pc:
            parts.append(f"{pc} pin issue(s)")
        if not parts:
            return "No issues found."
        return "Issues: " + ", ".join(parts) + "."

    def format(self) -> str:
        sections = [f"=== deplint report: {self.source_file} ==="]
        if self.version_result.has_conflicts():
            sections.append(str(self.version_result))
        if self.deprecated_result.has_issues():
            sections.append(str(self.deprecated_result))
        if self.security_result.has_issues():
            sections.append(str(self.security_result))
        if self.pin_result.has_issues():
            sections.append(str(self.pin_result))
        sections.append(self.summary())
        return "\n".join(sections)
