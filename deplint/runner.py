"""Orchestrate all checks against a list of dependencies."""
from __future__ import annotations

from typing import List

from deplint.parser import Dependency, parse_requirements
from deplint.report import AnalysisReport
from deplint.version_checker import check_versions
from deplint.license_checker import check_licenses
from deplint.deprecated_checker import check_deprecated
from deplint.security_checker import check_security
from deplint.outdated_checker import check_outdated
from deplint.pin_checker import check_pins
from deplint.duplicate_checker import check_duplicates
from deplint.yanked_checker import check_yanked
from deplint.extras_checker import check_extras
from deplint.python_version_checker import check_python_versions
from deplint.marker_checker import check_markers
from deplint.env_checker import check_env_markers


def run_all_checks(
    deps: List[Dependency],
    source_file: str = "<stdin>",
    allow_licenses: List[str] | None = None,
) -> AnalysisReport:
    """Run every available checker against *deps* and return a combined report."""
    results = [
        check_versions(deps),
        check_licenses(deps, allow_list=allow_licenses),
        check_deprecated(deps),
        check_security(deps),
        check_outdated(deps),
        check_pins(deps),
        check_duplicates(deps),
        check_yanked(deps),
        check_extras(deps),
        check_python_versions(deps),
        check_markers(deps),
        check_env_markers(deps),
    ]
    return AnalysisReport(source_file=source_file, results=results)


def run_checks_from_file(
    path: str,
    allow_licenses: List[str] | None = None,
) -> AnalysisReport:
    """Parse *path* as a requirements file and run all checks."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    deps = parse_requirements(content)
    return run_all_checks(deps, source_file=path, allow_licenses=allow_licenses)
