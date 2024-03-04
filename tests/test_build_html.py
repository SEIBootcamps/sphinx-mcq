from typing import TYPE_CHECKING
import pytest

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


@pytest.mark.sphinx_build("html", "test_html")
def test_html_output(build_contents: "BeautifulSoup"):
    assert build_contents is not None
    assert "Welcome to the Test Document" in build_contents.find("h1").text
