"""Sphinx extension for creating a cleaner ``toc`` (table of contents) of the
page's sections that doesn't include the page title, like the default ``toc``
context variable.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from bs4 import BeautifulSoup
from docutils import nodes
from sphinx.application import Sphinx

__all__ = ["process_html_page_context_for_toc"]


def process_html_page_context_for_toc(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: Dict[str, Any],
    doctree: Optional[nodes.document],
) -> None:
    """Process the HTML page context to add a new ``technote-toc`` context
    variable.

    This function is hooked into the Sphinx ``html-page-context`` event.
    """
    print(f"page: {pagename}")
    print(f"template: {templatename}")
    try:
        default_toc_html = context["toc"]
    except KeyError:
        # Pages like "search" won't have an existing toc
        context["technote_toc"] = ""
        return

    # print("default toc")
    # print(default_toc_html)

    context["technote_toc"] = transform_toc_html(default_toc_html)


def transform_toc_html(sphinx_toc: str) -> str:
    """Transform the Sphinx toc HTML for technotes.

    The transformation involves removing the top-level node for the page
    title and adding additional CSS classes.
    """
    soup = BeautifulSoup(sphinx_toc, "html.parser")
    root_list = soup.select_one("li > ul")

    return str(root_list)
