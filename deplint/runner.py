"""Run all configured checks against a list of dependencies."""
from typing import List, Optional
from deplint.parser import Dependency, parse_requirements
from deplint.version_checker import check_versions
from deplint.license_checker import check_licenses
from deplint.deprecated_checker import check_deprecated
from deplint.security_checker import check_security
from deplint.outdated_checker import check_outdated
from deplint.report import AnalysisReport


def run_all_checks(
    deps: List[Dependency],
    source_file: str = "<unknown>",
    allow_licenses: Optional[List[str]] = None,
    check_outdated_versions: bool = False,
    pypi_info_map: Optional[dict] = None,
) -> AnalysisReport:
    """Run all checks on the given dependency list and return a report."""
    version_result = check_versions(deps)
    license_result = check_licenses(deps, allow_list=allow_licenses)
    deprecated_result = check_deprecated(deps)
    security_result = check_security(deps)

    if check_outdated_versions:
        outdated_result = check_outdated(deps, info_map=pypi_info_map)
    else:
        from deplint.outdated_checker import OutdatedCheckResult
        outdated_result = OutdatedCheckResult()

    return AnalysisReport(
        source_file=source_file,
        version_result=version_result,
        license_result=license_result,
        deprecated_result=deprecated_result,
        security_result=security_result,
        outdated_result=outdated_result,
    )


def run_checks_from_file(
    path: str,
    allow_licenses: Optional[List[str]] = None,
    check_outdated_versions: bool = False,
) -> AnalysisReport:
    """Parse a requirements file and run all checks."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    deps = parse_requirements(content)
    return run_all_checks(
        deps,
        source_file=path,
        allow_licenses=allow_licenses,
        check_outdated_versions=check_outdated_versions,
    )
