"""sphinx_mcq

Sphinx extension for building multiple choice questions.

Example::

   .. mcq:: Write your question statement here.
      :numbered:
      :answer: B

      You can add additional text for the prompt too.

      A. Answer one

         :feedback: Use this field list syntax to explain why this answer is
                    right/wrong.

      B. Answer two

         :feedback: Use this field list syntax to explain why this answer is
                    right/wrong.

      C. Answer three

         :feedback: Use this field list syntax to explain why this answer is
                    right/wrong.
"""

from typing import TYPE_CHECKING

from os import path
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.osutil import copyfile, ensuredir

if TYPE_CHECKING:
    from typing import List
    from sphinx.application import Sphinx

from .transforms import MCQChoices, MCQFeedback
from .addnodes import mcq, mcq_body
from . import addnodes, builder

logger = logging.getLogger(__name__)

module_dir = Path(path.abspath(path.dirname(__file__)))
assets_dir = (module_dir / "assets").resolve()
css_files = [
    ("mcq-styles.css", {}),
]


class MCQDirective(SphinxDirective):
    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    node_class = mcq
    option_spec = {
        "answer": directives.unchanged,
        "class": directives.class_option,
        "name": directives.unchanged,
        "numbered": directives.flag,
        "show_feedback": directives.flag,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not getattr(self.env, "_mcq_count", None):
            self.env._mcq_count = 0
        self.env._mcq_count += 1

        # Create name if it doesn't exist
        if not self.options.get("name"):
            self.options["name"] = f"mcq-{self.env._mcq_count}"

        # Parse flags in self.options to True/False
        for opt_name, opt_type in self.option_spec.items():
            if opt_type is directives.flag:
                self.options[opt_name] = opt_name in self.options

        # 'numbered' and 'show_feedback' options should become classes
        classes = self.options.setdefault("classes", [])
        if self.options.get("numbered"):
            classes.append("numbered")
        if self.options.get("show_feedback"):
            classes.append("show-feedback")

    def run(self) -> "List[mcq]":
        """Build an mcq node.

        Contents of mcq node/hierarchy should be:

        - mcq_body
          - children
        - mcq_choices_list
          - mcq_choice
            - children
            - mcq_feedback
        """

        node = mcq("\n".join(self.content), **self.options)
        self.add_name(node)

        # First argument becomes the prompt
        textnodes, _ = self.state.inline_text(self.arguments[0], self.lineno)
        question_prompt = nodes.paragraph(self.arguments[0], "", *textnodes)

        body = mcq_body("\n".join(self.content))
        self.state.nested_parse(self.content, self.content_offset, body)

        # Rearrange body.children so it starts with first_paragraph followed
        # by the rest of body.children. Then we can add body to node's children.
        body.children = [question_prompt, *body.children]
        node += body

        return [node]


def add_css_files(app: "Sphinx") -> None:
    """Add static files to Sphinx builder."""

    # Only add static files to enabled builders.
    if app.builder.name in app.config.mcq_builders:
        # Register CSS files with builder and copy to build output
        for f, opts in css_files:
            app.add_css_file(f, **opts)


def copy_css_files(app: "Sphinx", exception: Exception) -> None:
    """Copy CSS files into output directory."""

    if exception:
        return

    staticdir = (Path(app.builder.outdir) / "_static").resolve()
    for f in [file for file, *_ in css_files]:
        try:
            source = assets_dir / f
            dest = staticdir / Path(f).name
            ensuredir(str(dest.parent))
            copyfile(str(source), str(dest))
        except FileNotFoundError:
            logger.warning(f"Could not copy {f} to output directory.", color="yellow")


def setup(app: "Sphinx"):
    app.add_config_value("mcq_builders", ["html"], "html")
    app.connect("builder-inited", add_css_files)
    app.connect("build-finished", copy_css_files)
    addnodes.setup(app)
    app.add_directive("mcq", MCQDirective)
    app.add_transform(MCQChoices)
    app.add_transform(MCQFeedback)
    builder.setup(app)
