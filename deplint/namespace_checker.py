"""Check for packages that share a namespace, which can cause import conflicts."""

from dataclasses import dataclass, field
from typing import List
from deplint.parser import Dependency

# Known namespace conflicts: packages that share top-level import names
KNOWN_NAMESPACE_CONFLICTS = {
    "google": ["google-cloud-storage", "google-cloud-bigquery", "google-auth", "google-api-python-client"],
    "azure": ["azure-storage-blob", "azure-identity", "azure-mgmt-compute", "azure-core"],
    "boto": ["boto", "boto3", "botocore"],
    "zope": ["zope.interface", "zope.component", "zope.event"],
    "twisted": ["twisted", "twisted-iocpsupport"],
}


@dataclass
class NamespaceIssue:
    package: str
    namespace: str
    conflicting_packages: List[str]
    line_number: int

    def __str__(self) -> str:
        others = ", ".join(self.conflicting_packages)
        return (
            f"Line {self.line_number}: '{self.package}' shares namespace "
            f"'{self.namespace}' with: {others}. Ensure namespace packages are "
            f"compatible to avoid import conflicts."
        )


@dataclass
class NamespaceCheckResult:
    issues: List[NamespaceIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.issues:
            return "Namespace check: no issues found."
        lines = ["Namespace check issues:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def _normalize(name: str) -> str:
    return name.lower().replace("_", "-")


def check_namespaces(deps: List[Dependency]) -> NamespaceCheckResult:
    """Detect packages in the list that share a known conflicting namespace."""
    result = NamespaceCheckResult()
    normalized_present = {_normalize(d.name): d for d in deps}

    for dep in deps:
        norm_name = _normalize(dep.name)
        for namespace, conflict_group in KNOWN_NAMESPACE_CONFLICTS.items():
            norm_group = [_normalize(p) for p in conflict_group]
            if norm_name not in norm_group:
                continue
            # Find other packages from the same conflict group present in deps
            others_present = [
                p for p in conflict_group
                if _normalize(p) != norm_name and _normalize(p) in normalized_present
            ]
            if others_present:
                result.issues.append(
                    NamespaceIssue(
                        package=dep.name,
                        namespace=namespace,
                        conflicting_packages=others_present,
                        line_number=dep.line_number,
                    )
                )
                break  # only report one namespace conflict per package

    return result
