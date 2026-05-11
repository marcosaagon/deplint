"""Command-line interface for deplint."""

import argparse
import sys
from typing import List, Optional

from deplint.parser import parse_requirements
from deplint.version_checker import check_versions
from deplint.license_checker import check_licenses
from deplint.deprecated_checker import check_deprecations
from deplint.fetcher import fetch_licenses, fetch_classifiers_map


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deplint",
        description="Static analyzer for Python dependency files.",
    )
    parser.add_argument(
        "requirements",
        metavar="FILE",
        help="Path to requirements file (e.g. requirements.txt)",
    )
    parser.add_argument(
        "--skip-versions",
        action="store_true",
        help="Skip version conflict checks",
    )
    parser.add_argument(
        "--skip-licenses",
        action="store_true",
        help="Skip license checks",
    )
    parser.add_argument(
        "--skip-deprecated",
        action="store_true",
        help="Skip deprecated package checks",
    )
    parser.add_argument(
        "--allow-licenses",
        metavar="LICENSE",
        nargs="+",
        help="Allowlist of permitted SPDX license identifiers",
    )
    return parser


def run(args: Optional[List[str]] = None) -> int:
    parser = build_parser()
    parsed = parser.parse_args(args)

    try:
        with open(parsed.requirements, "r") as fh:
            content = fh.read()
    except FileNotFoundError:
        print(f"Error: file not found: {parsed.requirements}", file=sys.stderr)
        return 2

    dependencies = parse_requirements(content)
    exit_code = 0

    if not parsed.skip_versions:
        version_result = check_versions(dependencies)
        if version_result.has_conflicts():
            print(str(version_result))
            exit_code = 1

    if not parsed.skip_licenses:
        package_names = [dep.name for dep in dependencies]
        licenses = fetch_licenses(package_names)
        license_result = check_licenses(
            dependencies, licenses, allow_list=parsed.allow_licenses
        )
        if license_result.has_issues():
            print(str(license_result))
            exit_code = 1

    if not parsed.skip_deprecated:
        package_names = [dep.name for dep in dependencies]
        classifiers_map = fetch_classifiers_map(package_names)
        deprecated_result = check_deprecations(dependencies, classifiers_map=classifiers_map)
        if deprecated_result.has_issues():
            print(str(deprecated_result))
            exit_code = 1

    if exit_code == 0:
        print("All checks passed.")

    return exit_code


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
