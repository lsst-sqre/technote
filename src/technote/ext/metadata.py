"""Sphinx extension for introspecting and exporting technote metadata."""

from __future__ import annotations

from typing import Any, Dict, Optional

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.config import Config

from .abstract import AbstractNode

__all__ = ["get_title", "process_html_page_context_for_metadata"]


def get_title(
    *,
    app: Sphinx,
    context: Dict[str, Any],
    doctree: Optional[nodes.document],
    config: Config,
) -> None:
    """Get the H1 title to use as the technote title."""
    if doctree is not None:
        for title_node in doctree.findall(
            condition=lambda x: isinstance(x, nodes.title)
        ):
            title = title_node.astext()
            context["technote"].set_content_title(title)
            break


def get_abstract(
    *,
    app: Sphinx,
    context: Dict[str, Any],
    doctree: Optional[nodes.document],
    config: Config,
) -> None:
    if doctree is not None:
        for abstract_node in doctree.findall(
            condition=lambda x: isinstance(x, AbstractNode)
        ):
            content = abstract_node.astext()
            context["technote"].set_abstract(content)
            break


def process_html_page_context_for_metadata(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: Dict[str, Any],
    doctree: Optional[nodes.document],
) -> None:
    """Process the HTML page to prepare the context for the HTML templates.

    This function is hooked into the Sphinx ``html-page-context`` event.
    """
    get_title(app=app, context=context, doctree=doctree, config=app.config)
    get_abstract(app=app, context=context, doctree=doctree, config=app.config)
