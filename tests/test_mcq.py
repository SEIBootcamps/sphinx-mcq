from typing import TYPE_CHECKING
import pytest

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


@pytest.mark.sphinx_build("html", "test_mcq")
def test_html_output(build_contents: "BeautifulSoup"):
    assert build_contents is not None
    assert "Welcome to the Test Document" in build_contents.find("h1").text


@pytest.mark.sphinx_build("json", "test_mcq")
def test_json_output(build_contents):
    assert build_contents is not None
