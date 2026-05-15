"""Aggregate analysis report combining results from all checkers."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AnalysisReport:
    source_file: str = "<input>"
    version_result: Optional[object] = None
    license_result: Optional[object] = None
    deprecated_result: Optional[object] = None
    security_result: Optional[object] = None
    outdated_result: Optional[object] = None
    pin_result: Optional[object] = None
    duplicate_result: Optional[object] = None
    yanked_result: Optional[object] = None
    extras_result: Optional[object] = None

    def _results(self):
        return [
            self.version_result,
            self.license_result,
            self.deprecated_result,
            self.security_result,
            self.outdated_result,
            self.pin_result,
            self.duplicate_result,
            self.yanked_result,
            self.extras_result,
        ]

    def has_any_issues(self) -> bool:
        return any(r is not None and r.has_issues() for r in self._results())

    def summary(self) -> str:
        counts = {
            "version": self.version_result,
            "license": self.license_result,
            "deprecated": self.deprecated_result,
            "security": self.security_result,
            "outdated": self.outdated_result,
            "pin": self.pin_result,
            "duplicate": self.duplicate_result,
            "yanked": self.yanked_result,
            "extras": self.extras_result,
        }
        parts = []
        for name, result in counts.items():
            if result is not None and result.has_issues():
                n = len(result.issues)
                parts.append(f"{n} {name}")
        if not parts:
            return "No issues found."
        return "Issues: " + ", ".join(parts) + "."

    def format(self) -> str:
        lines = [f"=== deplint report: {self.source_file} ==="]
        lines.append(self.summary())
        label_map = [
            ("Version conflicts", self.version_result),
            ("License issues", self.license_result),
            ("Deprecated packages", self.deprecated_result),
            ("Security vulnerabilities", self.security_result),
            ("Outdated packages", self.outdated_result),
            ("Pinning issues", self.pin_result),
            ("Duplicates", self.duplicate_result),
            ("Yanked releases", self.yanked_result),
            ("Extras issues", self.extras_result),
        ]
        for label, result in label_map:
            if result is not None and result.has_issues():
                lines.append(f"\n[{label}]")
                for issue in result.issues:
                    lines.append(f"  {issue}")
        return "\n".join(lines)
