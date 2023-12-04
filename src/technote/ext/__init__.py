"""Sphinx extensions for Technote documents."""

from __future__ import annotations

from typing import Any

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
from .insertposttitle import insert_post_title
from .metadata import process_html_page_context_for_metadata
from .pygmentscss import overwrite_pygments_css
from .toc import process_html_page_context_for_toc
from .wraptables import wrap_html_tables

__all__ = ["setup"]


def setup(app: Sphinx) -> dict[str, Any]:
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

    app.connect("builder-inited", _add_js_file)

    app.connect("build-finished", wrap_html_tables)
    app.connect("build-finished", insert_post_title)
    app.connect("build-finished", overwrite_pygments_css)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def _add_js_file(app: Sphinx) -> None:
    """Add Technote's javascript to the Sphinx page."""
    app.add_js_file("scripts/technote.js")
