"""Parser for Python dependency files (requirements.txt format)."""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Dependency:
    """Represents a single parsed dependency entry."""

    name: str
    version_spec: str = ""
    extras: list[str] = field(default_factory=list)
    line_number: int = 0
    raw: str = ""

    def __str__(self) -> str:
        extras_str = f"[{','.join(self.extras)}]" if self.extras else ""
        return f"{self.name}{extras_str}{self.version_spec}"


# Matches: package[extra1,extra2]>=1.0,<2.0  (with optional comment)
_DEP_PATTERN = re.compile(
    r"^(?P<name>[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"(?:\[(?P<extras>[^\]]+)\])?"
    r"(?P<version_spec>[^#\s]*)\s*"
    r"(?:#.*)?$"
)


def parse_requirements(content: str) -> list[Dependency]:
    """Parse requirements.txt content and return a list of Dependency objects.

    Ignores blank lines, comments, and options (lines starting with '-').

    Args:
        content: Raw text content of a requirements file.

    Returns:
        List of parsed Dependency objects.
    """
    dependencies: list[Dependency] = []

    for lineno, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()

        # Skip empty lines, comments, and pip options
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            continue

        # Handle inline URLs / VCS references — skip gracefully
        if re.search(r"(https?://|git\+|svn\+|hg\+)", stripped):
            continue

        match = _DEP_PATTERN.match(stripped)
        if not match:
            continue

        name = match.group("name")
        extras_raw: Optional[str] = match.group("extras")
        extras = [e.strip() for e in extras_raw.split(",")] if extras_raw else []
        version_spec = match.group("version_spec").strip()

        dependencies.append(
            Dependency(
                name=name,
                version_spec=version_spec,
                extras=extras,
                line_number=lineno,
                raw=stripped,
            )
        )

    return dependencies
