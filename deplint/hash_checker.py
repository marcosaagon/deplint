"""Checker for missing or malformed hash pins in requirements."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from deplint.parser import Dependency

VALID_HASH_ALGORITHMS = {"sha256", "sha384", "sha512"}


@dataclass
class HashIssue:
    package: str
    line_number: int
    reason: str

    def __str__(self) -> str:
        return (
            f"Line {self.line_number}: {self.package} — {self.reason}"
        )


@dataclass
class HashCheckResult:
    issues: List[HashIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        if not self.has_issues():
            return "Hash check: OK"
        lines = ["Hash check issues:"]
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)


def _parse_hashes(raw_options: List[str]) -> List[tuple]:
    """Return list of (algorithm, value) pairs from option strings like '--hash=sha256:abc'."""
    hashes = []
    for opt in raw_options:
        if opt.startswith("--hash="):
            value = opt[len("--hash="):]
            if ":" in value:
                algo, digest = value.split(":", 1)
                hashes.append((algo.lower(), digest))
            else:
                hashes.append((value.lower(), ""))
    return hashes


def check_hashes(
    dependencies: List[Dependency],
    require_hashes: bool = False,
) -> HashCheckResult:
    """Check each dependency for hash correctness.

    Args:
        dependencies: Parsed dependency list.
        require_hashes: When True, flag any dependency that has no hash at all.
    """
    issues: List[HashIssue] = []

    for dep in dependencies:
        options: List[str] = getattr(dep, "options", []) or []
        hashes = _parse_hashes(options)

        if require_hashes and not hashes:
            issues.append(
                HashIssue(
                    package=dep.name,
                    line_number=dep.line_number,
                    reason="no hash specified (--require-hashes mode)",
                )
            )
            continue

        for algo, digest in hashes:
            if algo not in VALID_HASH_ALGORITHMS:
                issues.append(
                    HashIssue(
                        package=dep.name,
                        line_number=dep.line_number,
                        reason=f"unsupported hash algorithm '{algo}' (use sha256, sha384, or sha512)",
                    )
                )
            elif len(digest) == 0:
                issues.append(
                    HashIssue(
                        package=dep.name,
                        line_number=dep.line_number,
                        reason=f"empty hash digest for algorithm '{algo}'",
                    )
                )

    return HashCheckResult(issues=issues)
