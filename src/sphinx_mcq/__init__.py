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

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:
    from typing import List
    from sphinx.application import Sphinx

from .transforms import MCQChoices, MCQFeedback
from .addnodes import mcq, mcq_body
from . import addnodes, builder

logger = logging.getLogger(__name__)


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


def setup(app: "Sphinx"):
    addnodes.setup(app)
    app.add_directive("mcq", MCQDirective)
    app.add_transform(MCQChoices)
    app.add_transform(MCQFeedback)
    builder.setup(app)
