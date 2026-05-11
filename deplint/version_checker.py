"""Version conflict detection for dependency files."""

from dataclasses import dataclass, field
from typing import List, Optional
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet

from deplint.parser import Dependency


@dataclass
class VersionConflict:
    package: str
    specifiers: List[str]
    message: str

    def __str__(self) -> str:
        specs = ", ".join(self.specifiers)
        return f"[version-conflict] {self.package} ({specs}): {self.message}"


@dataclass
class CheckResult:
    conflicts: List[VersionConflict] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def __str__(self) -> str:
        if not self.has_conflicts:
            return "No version conflicts detected."
        return "\n".join(str(c) for c in self.conflicts)


def _is_conflicting_specifier_set(specifier_str: str) -> Optional[str]:
    """Check if a specifier set contains contradictory constraints."""
    try:
        spec_set = SpecifierSet(specifier_str)
    except Exception:
        return f"Invalid specifier: '{specifier_str}'"

    lower_bound: Optional[Version] = None
    upper_bound: Optional[Version] = None

    for spec in spec_set:
        try:
            v = Version(spec.version)
        except InvalidVersion:
            continue

        if spec.operator in (">=", ">"):
            if lower_bound is None or v > lower_bound:
                lower_bound = v
        elif spec.operator in (">=", "<=", "<"):
            if upper_bound is None or v < upper_bound:
                upper_bound = v

    if lower_bound is not None and upper_bound is not None:
        if lower_bound >= upper_bound:
            return (
                f"lower bound {lower_bound} is not compatible "
                f"with upper bound {upper_bound}"
            )

    return None


def check_version_conflicts(dependencies: List[Dependency]) -> CheckResult:
    """Detect version conflicts within a list of dependencies."""
    result = CheckResult()
    seen: dict = {}

    for dep in dependencies:
        name_lower = dep.name.lower()
        if name_lower in seen:
            existing = seen[name_lower]
            result.conflicts.append(
                VersionConflict(
                    package=dep.name,
                    specifiers=[str(existing.version_spec), str(dep.version_spec)],
                    message="package declared multiple times",
                )
            )
        else:
            seen[name_lower] = dep

        if dep.version_spec:
            reason = _is_conflicting_specifier_set(dep.version_spec)
            if reason:
                result.conflicts.append(
                    VersionConflict(
                        package=dep.name,
                        specifiers=[dep.version_spec],
                        message=reason,
                    )
                )

    return result
