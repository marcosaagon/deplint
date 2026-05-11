"""Command-line interface for deplint."""

import sys
import argparse
from pathlib import Path

from deplint.parser import parse_requirements
from deplint.version_checker import check_version_conflicts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deplint",
        description="Static analyzer for Python dependency files.",
    )
    parser.add_argument(
        "requirements",
        nargs="?",
        default="requirements.txt",
        help="Path to requirements file (default: requirements.txt)",
    )
    parser.add_argument(
        "--no-version-check",
        action="store_true",
        help="Skip version conflict detection",
    )
    parser.add_argument(
        "--exit-zero",
        action="store_true",
        help="Always exit with code 0 even when issues are found",
    )
    return parser


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    req_path = Path(args.requirements)
    if not req_path.exists():
        print(f"deplint: error: file not found: {req_path}", file=sys.stderr)
        return 1

    with req_path.open() as fh:
        content = fh.read()

    dependencies = parse_requirements(content)
    print(f"Parsed {len(dependencies)} dependencies from {req_path}")

    exit_code = 0

    if not args.no_version_check:
        result = check_version_conflicts(dependencies)
        if result.has_conflicts:
            print("\nVersion conflicts found:")
            print(result)
            exit_code = 1
        else:
            print("No version conflicts detected.")

    return 0 if args.exit_zero else exit_code


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
