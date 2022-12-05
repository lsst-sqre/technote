"""Sphinx extension for introspecting and exporting technote metadata."""

from __future__ import annotations

from typing import Any, Dict, Optional

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.config import Config

from .abstract import AbstractNode

__all__ = [
    "process_html_page_context_for_metadata",
    "get_abstract",
    "get_title",
    "set_html_title",
]


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
    """Get the abstract as plain text from the abstract directive."""
    if doctree is not None:
        for abstract_node in doctree.findall(
            condition=lambda x: isinstance(x, AbstractNode)
        ):
            content = abstract_node.astext()
            context["technote"].set_abstract(content)
            break


def set_html_title(*, context: Dict[str, Any]) -> None:
    """Set the ``html_title`` and ``project`` metadata based on the
    title metadata, resolved from either technote.toml or the content's
    top-level heading.
    """
    context["title"] = context["technote"].title


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

    set_html_title(context=context)
