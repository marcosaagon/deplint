"""Integration tests: parse a requirements string then run circular check."""
from deplint.parser import parse_requirements
from deplint.circular_checker import check_circular


def _parse(text: str):
    import io
    return parse_requirements(io.StringIO(text))


def test_integration_clean_requirements_no_issues():
    text = "requests==2.31.0\nflask>=2.0\nclick==8.1.3\n"
    deps = _parse(text)
    result = check_circular(deps)
    assert not result.has_issues()


def test_integration_detects_pip_in_requirements():
    text = "requests==2.31.0\npip==23.1\n"
    deps = _parse(text)
    result = check_circular(deps)
    assert result.has_issues()
    names = [i.package.lower() for i in result.issues]
    assert "pip" in names


def test_integration_detects_setuptools_in_requirements():
    text = "setuptools==68.0.0\nrequests==2.31.0\n"
    deps = _parse(text)
    result = check_circular(deps)
    assert result.has_issues()
    assert result.issues[0].package == "setuptools"


def test_integration_line_numbers_are_positive():
    text = "# comment\nsetuptools==68.0.0\n"
    deps = _parse(text)
    result = check_circular(deps)
    assert result.has_issues()
    assert result.issues[0].line_number > 0


def test_integration_result_str_lists_all_flagged_packages():
    text = "pip==23.1\nwheel==0.41.0\nrequests==2.31.0\n"
    deps = _parse(text)
    result = check_circular(deps)
    text_out = str(result)
    assert "pip" in text_out
    assert "wheel" in text_out
