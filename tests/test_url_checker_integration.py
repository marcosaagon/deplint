"""Integration tests: parse a requirements string then run the URL checker."""

from io import StringIO
from deplint.parser import parse_requirements
from deplint.url_checker import check_url_dependencies


_REQUIREMENTS_WITH_URLS = """\
requests==2.28.0
flask>=2.0,<3.0
# a comment
mylib @ git+https://github.com/user/mylib.git@v1.2.3
legacy http://internal.corp/legacy-1.0.tar.gz
numpy==1.24.0
"""

_CLEAN_REQUIREMENTS = """\
requests==2.28.0
flask>=2.0,<3.0
numpy==1.24.0
click==8.1.3
"""


def _parse(text: str):
    return parse_requirements(StringIO(text))


def test_integration_detects_url_deps_in_requirements():
    deps = _parse(_REQUIREMENTS_WITH_URLS)
    result = check_url_dependencies(deps)
    # At least one URL-based dep should be flagged
    assert result.has_issues(), "Expected URL issues but found none"
    flagged = {i.package for i in result.issues}
    # 'mylib' uses git+ scheme; 'legacy' uses http://
    assert "mylib" in flagged or "legacy" in flagged


def test_integration_clean_requirements_no_issues():
    deps = _parse(_CLEAN_REQUIREMENTS)
    result = check_url_dependencies(deps)
    assert not result.has_issues()


def test_integration_issue_line_numbers_are_positive():
    deps = _parse(_REQUIREMENTS_WITH_URLS)
    result = check_url_dependencies(deps)
    for issue in result.issues:
        assert issue.line_number > 0


def test_integration_result_str_lists_all_flagged_packages():
    deps = _parse(_REQUIREMENTS_WITH_URLS)
    result = check_url_dependencies(deps)
    output = str(result)
    for issue in result.issues:
        assert issue.package in output
