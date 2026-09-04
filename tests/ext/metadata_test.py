"""Tests for the technote.ext.metadata module."""

from __future__ import annotations

from pathlib import Path
from typing import IO

import lxml.html
import pytest
from docutils import nodes
from docutils.utils import new_document
from sphinx.application import Sphinx
from sphinx.util import logging

from technote.ext.metadata import resolve_title
from technote.templating.context import TechnoteJinjaContext


def technote_context(app: Sphinx) -> TechnoteJinjaContext:
    """Get the TechnoteJinjaContext that the sphinxconf module registered."""
    return app.config.html_context["technote"]


@pytest.mark.sphinx("dummy", testroot="title-from-content")
def test_title_from_content_dummy_builder(
    app: Sphinx, status: IO, warning: IO
) -> None:
    """A technote without a TOML title gets its title from the document's H1
    after the read phase, even for a builder that never writes HTML.
    """
    app.verbosity = 2
    logging.setup(app, status, warning)
    app.builder.build_all()

    metadata = technote_context(app).metadata
    assert metadata.title == "Title from the H1 heading"


@pytest.mark.sphinx("dummy", testroot="metadata-basic")
def test_toml_title_wins_dummy_builder(
    app: Sphinx, status: IO, warning: IO
) -> None:
    """A title set in technote.toml is not overridden by the document's H1
    ("Metadata demonstration" in this test root).
    """
    app.verbosity = 2
    logging.setup(app, status, warning)
    app.builder.build_all()

    metadata = technote_context(app).metadata
    assert metadata.title == "Metadata test document"


@pytest.mark.sphinx("html", testroot="title-from-content")
def test_title_from_content_html(app: Sphinx, status: IO, warning: IO) -> None:
    """The HTML page publishes the H1 as the title metadata."""
    app.verbosity = 2
    logging.setup(app, status, warning)
    app.builder.build_all()

    html_source = Path(app.outdir).joinpath("index.html").read_text()
    doc = lxml.html.document_fromstring(html_source)

    assert doc.cssselect("title")[0].text == "Title from the H1 heading"
    assert (
        doc.cssselect("meta[name='citation_title']")[0].get("content")
        == "Title from the H1 heading"
    )
    assert technote_context(app).metadata.title == "Title from the H1 heading"


def test_resolve_title() -> None:
    """The title is the text of the first title node."""
    doctree = new_document("<test>")
    section = nodes.section()
    section += nodes.title(text="The document title")
    section += nodes.paragraph(text="Body.")
    subsection = nodes.section()
    subsection += nodes.title(text="A subsection")
    section += subsection
    doctree += section

    assert resolve_title(doctree) == "The document title"


def test_resolve_title_without_heading() -> None:
    """A document with no heading has no title."""
    doctree = new_document("<test>")
    doctree += nodes.paragraph(text="Body only.")

    assert resolve_title(doctree) is None
