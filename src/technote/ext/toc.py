"""Sphinx extension for creating a cleaner ``toc`` (table of contents) of the
page's sections that doesn't include the page title, like the default ``toc``
context variable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from docutils import nodes
from sphinx.application import Sphinx

from .abstract import AbstractNode

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

    prepend_sections: List[SyntheticTocSection] = []

    # Find an abstract node, which isn't collected by Sphinx for the local toc
    if doctree:
        child_abstracts = list(doctree.findall(condition=AbstractNode))
        if len(child_abstracts) > 0:
            prepend_sections.append(
                SyntheticTocSection(label="Abstract", href="#abstract")
            )

    context["technote_toc"] = transform_toc_html(
        default_toc_html, prepend_sections=prepend_sections
    )


def transform_toc_html(
    sphinx_toc: str,
    prepend_sections: Optional[List[SyntheticTocSection]] = None,
) -> str:
    """Transform the Sphinx toc HTML for technotes.

    The transformation involves removing the top-level node for the page
    title and adding additional CSS classes.
    """
    soup = BeautifulSoup(sphinx_toc, "html.parser")
    root_list = soup.select_one("li > ul")

    if prepend_sections:
        # reverse order to so we can insert at index 0
        for section in prepend_sections[::-1]:
            content = f'<li><a href="{section.href}">{section.label}</a></li>'
            new_tag = BeautifulSoup(content, "html.parser")
            root_list.insert(0, new_tag)

    return str(root_list)


@dataclass
class SyntheticTocSection:
    """An extra section in the TOC outline that wasn't found by Sphinx's
    toc collector (like the abstract).
    """

    label: str
    """The section name"""

    href: str
    """The section href."""
