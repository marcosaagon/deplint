"""Parser for pip-style requirements.txt files."""
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Dependency:
    name: str
    version_spec: Optional[str] = None
    extras: List[str] = field(default_factory=list)
    line_number: Optional[int] = None
    raw: str = ""

    def __str__(self) -> str:
        extras_str = f"[{','.join(self.extras)}]" if self.extras else ""
        spec = self.version_spec or ""
        return f"{self.name}{extras_str}{spec}"


# e.g. requests[security,socks]==2.28.0
_DEP_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9_.-]+)"
    r"(?:\[(?P<extras>[^\]]+)\])?"
    r"(?P<spec>[^;#\s]*)?"
    r"(?:\s*#.*)?$"
)


def parse_requirements(text: str) -> List[Dependency]:
    """Parse a requirements.txt string into a list of Dependency objects."""
    deps: List[Dependency] = []
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        # Strip inline comments
        line_no_comment = re.sub(r"\s*#.*$", "", line).strip()
        m = _DEP_RE.match(line_no_comment)
        if not m:
            continue
        name = m.group("name")
        extras_raw = m.group("extras") or ""
        extras = [e.strip() for e in extras_raw.split(",") if e.strip()]
        spec = m.group("spec") or None
        if spec == "":
            spec = None
        deps.append(
            Dependency(
                name=name,
                version_spec=spec,
                extras=extras,
                line_number=lineno,
                raw=raw_line,
            )
        )
    return deps
