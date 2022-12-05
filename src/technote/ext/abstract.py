"""Support for abstracts in technotes."""

from __future__ import annotations

from typing import List

from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator

__all__ = [
    "AbstractDirective",
    "AbstractNode",
    "visit_abstract_node_html",
    "depart_abstract_node_html",
]


class AbstractNode(nodes.General, nodes.Element):
    """A docutils node for the abstract content section."""


def visit_abstract_node_html(
    self: HTML5Translator, node: nodes.Element
) -> None:
    """Add HTML content before the `AbstractNode`."""
    self.body.append('<section class="technote-abstract" id="abstract">')
    self.body.append('<h2 class="technote-abstract__header">Abstract</h2>')


def depart_abstract_node_html(
    self: HTML5Translator, node: nodes.Element
) -> None:
    """Add HTML content after the `AbstractNode`."""
    self.body.append("</section>")


def visit_abstract_node_tex(
    self: LaTeXTranslator, node: nodes.Element
) -> None:
    """Add LaTeX content before the `AbstractNode`."""
    self.body.append(r"\begin{abstract}")


def depart_abstract_node_tex(
    self: LaTeXTranslator, node: nodes.Element
) -> None:
    """Add LaTeX content after the `AbstractNode`."""
    self.body.append(r"\end{abstract}")


class AbstractDirective(SphinxDirective):
    """The ``abstract`` directive for marking up a technote's summary."""

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = True

    def run(self) -> List[nodes.Node]:
        """Run the directive on content."""
        abstract_node = AbstractNode("\n".join(self.content))
        self.state.nested_parse(
            self.content, self.content_offset, abstract_node
        )
        return [abstract_node]
