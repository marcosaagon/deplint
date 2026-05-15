"""Run all checks against a list of dependencies or a requirements file."""

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
from deplint.env_checker import check_env_conflicts
from deplint.hash_checker import check_hashes
from deplint.url_checker import check_urls
from deplint.namespace_checker import check_namespaces


def run_all_checks(deps: List[Dependency], source_file: str = "<input>") -> AnalysisReport:
    """Run every available checker against deps and return an AnalysisReport."""
    report = AnalysisReport(source_file=source_file)

    report.add(check_versions(deps))
    report.add(check_licenses(deps))
    report.add(check_deprecated(deps))
    report.add(check_security(deps))
    report.add(check_outdated(deps))
    report.add(check_pins(deps))
    report.add(check_duplicates(deps))
    report.add(check_yanked(deps))
    report.add(check_extras(deps))
    report.add(check_python_versions(deps))
    report.add(check_markers(deps))
    report.add(check_env_conflicts(deps))
    report.add(check_hashes(deps))
    report.add(check_urls(deps))
    report.add(check_namespaces(deps))

    return report


def run_checks_from_file(path: str) -> AnalysisReport:
    """Parse a requirements file and run all checks, returning the report."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    deps = parse_requirements(content)
    return run_all_checks(deps, source_file=path)
