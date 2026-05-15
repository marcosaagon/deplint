"""Orchestrates all checks against a parsed requirements file."""
from typing import List, Optional

from deplint.parser import Dependency, parse_requirements
from deplint.version_checker import check_versions
from deplint.license_checker import check_licenses
from deplint.deprecated_checker import check_deprecated
from deplint.security_checker import check_security
from deplint.outdated_checker import check_outdated
from deplint.pin_checker import check_pins
from deplint.duplicate_checker import check_duplicates
from deplint.yanked_checker import check_yanked
from deplint.extras_checker import check_extras
from deplint.report import AnalysisReport


def run_all_checks(
    dependencies: List[Dependency],
    source_file: str = "<input>",
    package_info: Optional[dict] = None,
    allow_licenses: Optional[list] = None,
) -> AnalysisReport:
    """Run every available check and return a combined report."""
    info = package_info or {}

    return AnalysisReport(
        source_file=source_file,
        version_result=check_versions(dependencies),
        license_result=check_licenses(dependencies, info, allow_list=allow_licenses),
        deprecated_result=check_deprecated(dependencies),
        security_result=check_security(dependencies),
        outdated_result=check_outdated(dependencies, info),
        pin_result=check_pins(dependencies),
        duplicate_result=check_duplicates(dependencies),
        yanked_result=check_yanked(dependencies, info),
        extras_result=check_extras(dependencies),
    )


def run_checks_from_file(
    path: str,
    package_info: Optional[dict] = None,
    allow_licenses: Optional[list] = None,
) -> AnalysisReport:
    """Parse a requirements file from disk and run all checks."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    deps = parse_requirements(text)
    return run_all_checks(
        deps,
        source_file=path,
        package_info=package_info,
        allow_licenses=allow_licenses,
    )
