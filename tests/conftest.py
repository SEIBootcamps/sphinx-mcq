import pytest
from bs4 import BeautifulSoup
from sphinx.cmd.build import build_main
from pathlib import Path

pytest_plugins = "sphinx.testing.fixtures"
collect_ignore = ["roots"]


def pytest_configure(config):
    config.addinivalue_line("markers", "builder(name): mark test on specific builder")


@pytest.fixture
def build_contents(request):
    marker = request.node.get_closest_marker("sphinx_build")

    if marker is None:
        return None
    else:
        builder = marker.args[0]
        build_dir = marker.args[1]
        example_dir = (Path(__file__).parent / "examples" / build_dir).resolve()
        argv = [
            "-b",
            builder,
            str(example_dir),
            str(example_dir / "_build"),
        ]

        try:
            build_main(argv)
        except Exception as e:
            raise e

        if builder == "html":
            with open(example_dir / "_build" / "index.html") as f:
                contents = f.read()

            return BeautifulSoup(contents, "html.parser")
        if builder == "json":
            return "hi"
