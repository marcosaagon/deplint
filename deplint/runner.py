"""Orchestrates all checks across a requirements file."""

from deplint.parser import parse_requirements
from deplint.version_checker import check_conflicts
from deplint.license_checker import check_licenses
from deplint.deprecated_checker import check_deprecated
from deplint.security_checker import check_security
from deplint.outdated_checker import check_outdated
from deplint.pin_checker import check_pins
from deplint.duplicate_checker import check_duplicates
from deplint.report import AnalysisReport


def run_all_checks(dependencies, source_file: str = "") -> AnalysisReport:
    """Run all available checks on a list of Dependency objects."""
    version_result = check_conflicts(dependencies)
    license_result = check_licenses(dependencies)
    deprecated_result = check_deprecated(dependencies)
    security_result = check_security(dependencies)
    outdated_result = check_outdated(dependencies)
    pin_result = check_pins(dependencies)
    duplicate_result = check_duplicates(dependencies)

    return AnalysisReport(
        source_file=source_file,
        version_result=version_result,
        license_result=license_result,
        deprecated_result=deprecated_result,
        security_result=security_result,
        outdated_result=outdated_result,
        pin_result=pin_result,
        duplicate_result=duplicate_result,
    )


def run_checks_from_file(path: str) -> AnalysisReport:
    """Parse a requirements file and run all checks on its contents."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    dependencies = parse_requirements(content)
    return run_all_checks(dependencies, source_file=path)
