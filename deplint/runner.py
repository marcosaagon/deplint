"""High-level runner that orchestrates all checks and produces a report."""

from typing import List, Optional
from deplint.parser import parse_requirements, Dependency
from deplint.version_checker import check_versions
from deplint.license_checker import check_licenses
from deplint.deprecated_checker import check_deprecated
from deplint.security_checker import check_security
from deplint.report import AnalysisReport


def run_all_checks(
    dependencies: List[Dependency],
    source_file: Optional[str] = None,
    allow_licenses: Optional[List[str]] = None,
) -> AnalysisReport:
    """Run all available checks on a list of dependencies."""
    version_result = check_versions(dependencies)
    license_result = check_licenses(dependencies, allow_list=allow_licenses)
    deprecated_result = check_deprecated(dependencies)
    security_result = check_security(dependencies)

    return AnalysisReport(
        version_result=version_result,
        license_result=license_result,
        deprecated_result=deprecated_result,
        security_result=security_result,
        source_file=source_file,
    )


def run_checks_from_file(
    filepath: str,
    allow_licenses: Optional[List[str]] = None,
) -> AnalysisReport:
    """Parse a requirements file and run all checks."""
    with open(filepath, "r") as fh:
        content = fh.read()
    dependencies = parse_requirements(content)
    return run_all_checks(
        dependencies,
        source_file=filepath,
        allow_licenses=allow_licenses,
    )
