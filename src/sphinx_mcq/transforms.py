from typing import TYPE_CHECKING, cast
from docutils import nodes
from sphinx.transforms import SphinxTransform
from sphinx.util.docfields import _is_single_paragraph

from .addnodes import mcq, mcq_choices_list, mcq_choice, mcq_choice_feedback

if TYPE_CHECKING:
    from typing import Any


class MCQChoices(SphinxTransform):
    default_priority = 200
    choice_indexes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def apply(self, **kwargs: "Any") -> None:
        for mcq_node in self.document.findall(mcq, include_self=False):
            for answer_choices in mcq_node.findall(
                condition=lambda n: isinstance(n, nodes.enumerated_list)
                and n.get("enumtype") == "upperalpha",
                include_self=False,
            ):
                gen_choice_index = iter(self.choice_indexes)
                # Transform list_item node to mcq_choice node
                for item in answer_choices.children:
                    choice_node = mcq_choice("", *item.children)
                    choice_node.update_all_atts(item)

                    choice_node["mcq_id"] = mcq_node["ids"][0]
                    choice_node["value"] = next(gen_choice_index)
                    choice_node["mcq_is_correct"] = (
                        choice_node["value"] == mcq_node["answer"]
                    )

                    item.replace_self(choice_node)
                answer_choices.replace_self(
                    mcq_choices_list("", *answer_choices.children)
                )


def is_feedback_field(node: "nodes.Node") -> bool:
    def _has_feedback_field(node):
        field_name, *_ = node.children
        return (
            isinstance(field_name, nodes.field_name)
            and field_name.astext().strip().lower() == "feedback"
        )

    return isinstance(node, nodes.field) and _has_feedback_field(node)


class MCQFeedback(SphinxTransform):
    default_priority = 201

    def apply(self, **kwargs: "Any") -> None:
        for choice_node in self.document.findall(mcq_choice):
            for feedback_field in choice_node.findall(is_feedback_field):
                content = []
                field_name, field_body = feedback_field.children

                if (
                    isinstance(field_name, nodes.field_name)
                    and field_name.astext().strip().lower() == "feedback"
                ):
                    if _is_single_paragraph(field_body):
                        paragraph = cast(nodes.paragraph, field_body[0])
                        content = paragraph.children
                    else:
                        content = field_body.children

                # Replace field list with mcq_choice_feedback node
                feedback_field.parent.replace_self(
                    mcq_choice_feedback(
                        "",
                        nodes.paragraph("", "", *content),
                        is_correct=choice_node["mcq_is_correct"],
                    )
                )
