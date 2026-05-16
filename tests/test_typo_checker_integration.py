"""Integration tests: parse a requirements string then run typo checker."""
from deplint.parser import parse_requirements
from deplint.typo_checker import check_typos


def _parse(text: str):
    import io
    return parse_requirements(io.StringIO(text))


def test_integration_clean_requirements_no_issues():
    content = "requests==2.31.0\ndjango==4.2.0\nnumpy==1.26.0\n"
    deps = _parse(content)
    result = check_typos(deps)
    assert not result.has_issues()


def test_integration_detects_typo_in_requirements():
    content = "requets==2.31.0\ndjango==4.2.0\n"
    deps = _parse(content)
    result = check_typos(deps)
    assert result.has_issues()
    assert any(i.package == "requets" for i in result.issues)


def test_integration_line_numbers_are_correct():
    content = "requests==2.31.0\nflask==2.0.0\nnumpy==1.26.0\n"
    deps = _parse(content)
    result = check_typos(deps)
    assert result.has_issues()
    flagged = result.issues[0]
    assert flagged.line_number == 2


def test_integration_multiple_typos_in_file():
    content = "numppy==1.0\nrequets==2.0\ndjango==4.2\npandes==1.5\n"
    deps = _parse(content)
    result = check_typos(deps)
    assert len(result.issues) == 3


def test_integration_result_str_lists_all_flagged_packages():
    content = "flask==1.0\ncelrey==4.0\n"
    deps = _parse(content)
    result = check_typos(deps)
    output = str(result)
    assert "flask" in output
    assert "celrey" in output
