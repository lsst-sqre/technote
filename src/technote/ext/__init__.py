"""Sphinx extensions for Technote documents."""

from __future__ import annotations

from typing import Any, Dict

from sphinx.application import Sphinx

from technote import __version__

from .abstract import (
    AbstractDirective,
    AbstractNode,
    depart_abstract_node_html,
    depart_abstract_node_tex,
    visit_abstract_node_html,
    visit_abstract_node_tex,
)
from .metadata import process_html_page_context_for_metadata
from .toc import process_html_page_context_for_toc

__all__ = ["setup"]


def setup(app: Sphinx) -> Dict[str, Any]:
    """Set up Technote's own Sphinx extensions; these are automatically loaded
    in all technotes by default.
    """
    # Abstract
    app.add_directive("abstract", AbstractDirective)
    app.add_node(
        AbstractNode,
        html=(visit_abstract_node_html, depart_abstract_node_html),
        latex=(visit_abstract_node_tex, depart_abstract_node_tex),
    )

    # Metadata
    app.connect("html-page-context", process_html_page_context_for_metadata)
    app.connect("html-page-context", process_html_page_context_for_toc)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
