"""Sphinx extension for introspecting and exporting technote metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment

from .abstract import AbstractNode

if TYPE_CHECKING:
    from ..templating.context import TechnoteJinjaContext

__all__ = [
    "process_html_page_context_for_metadata",
    "resolve_title",
    "set_title_from_environment",
    "get_abstract",
    "get_title",
    "set_html_title",
]


def resolve_title(doctree: nodes.document) -> str | None:
    """Resolve the document's title from its content.

    The title is the plain text of the first ``title`` node in the doctree,
    which is the document's top-level (H1) heading.

    Parameters
    ----------
    doctree
        The document's doctree.

    Returns
    -------
    str or None
        The document's title, or `None` if the document has no heading.
    """
    for title_node in doctree.findall(nodes.title):
        return title_node.astext()
    return None


def set_title_from_environment(app: Sphinx, env: BuildEnvironment) -> None:
    """Set the technote title from the root document's H1 once the read
    phase is complete.

    This function is hooked into the Sphinx ``env-updated`` event, which
    fires for every builder. It reads the root document's doctree from the
    environment, so it also works for incremental builds where the root
    document was not re-read. The title in ``technote.toml`` is never
    overridden.
    """
    technote_context = _get_technote_context(app)
    if technote_context is None:
        return
    if app.config.root_doc not in env.all_docs:
        return
    title = resolve_title(env.get_doctree(app.config.root_doc))
    if title is not None:
        technote_context.set_content_title(title)


def _get_technote_context(app: Sphinx) -> TechnoteJinjaContext | None:
    """Get the `TechnoteJinjaContext` from the ``html_context``
    configuration, or `None` if the project is not configured as a technote.
    """
    html_context = getattr(app.config, "html_context", None)
    if not isinstance(html_context, dict):
        return None
    return html_context.get("technote")


def get_title(
    *,
    app: Sphinx,
    context: dict[str, Any],
    doctree: nodes.document | None,
    config: Config,
) -> None:
    """Get the H1 title to use as the technote title."""
    if doctree is not None:
        title = resolve_title(doctree)
        if title is not None:
            context["technote"].set_content_title(title)


def get_abstract(
    *,
    app: Sphinx,
    context: dict[str, Any],
    doctree: nodes.document | None,
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


def set_html_title(*, context: dict[str, Any]) -> None:
    """Set the ``html_title`` and ``project`` metadata based on the
    title metadata, resolved from either technote.toml or the content's
    top-level heading.
    """
    context["title"] = context["technote"].title


def process_html_page_context_for_metadata(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: nodes.document | None,
) -> None:
    """Process the HTML page to prepare the context for the HTML templates.

    This function is hooked into the Sphinx ``html-page-context`` event.
    """
    get_title(app=app, context=context, doctree=doctree, config=app.config)
    get_abstract(app=app, context=context, doctree=doctree, config=app.config)

    set_html_title(context=context)
