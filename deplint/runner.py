"""Orchestrates all checks across a parsed dependency list."""

from typing import List
from deplint.parser import Dependency, parse_requirements
from deplint.version_checker import check_versions
from deplint.deprecated_checker import check_deprecated
from deplint.security_checker import check_security
from deplint.pin_checker import check_pins
from deplint.report import AnalysisReport


def run_all_checks(
    deps: List[Dependency],
    source_file: str = "<unknown>",
    skip_network: bool = False,
) -> AnalysisReport:
    """Run all static and optional network checks and return a combined report."""
    version_result = check_versions(deps)
    deprecated_result = check_deprecated(deps)
    security_result = check_security(deps)
    pin_result = check_pins(deps)

    return AnalysisReport(
        source_file=source_file,
        version_result=version_result,
        deprecated_result=deprecated_result,
        security_result=security_result,
        pin_result=pin_result,
    )


def run_checks_from_file(path: str, skip_network: bool = False) -> AnalysisReport:
    """Parse a requirements file and run all checks."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    deps = parse_requirements(content)
    return run_all_checks(deps, source_file=path, skip_network=skip_network)
