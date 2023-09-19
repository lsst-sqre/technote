"""Test the representation of metadata in the generated site."""

from __future__ import annotations

from pathlib import Path
from typing import IO, Any

import lxml.html
import pytest
from sphinx.application import Sphinx
from sphinx.util import logging


@pytest.mark.sphinx("html", testroot="metadata-basic")
def test_metadata_basic(app: Sphinx, status: IO, warning: IO) -> None:
    """Test against the ``test-metadata-basic`` test root for metadata
    representation.
    """
    app.verbosity = 2
    logging.setup(app, status, warning)
    app.builder.build_all()

    html_source = Path(app.outdir).joinpath("index.html").read_text()
    doc = lxml.html.document_fromstring(html_source)

    # Test for HighWire metadata tags
    assert_tag(doc, "citation_title", "Metadata test document")
    assert_tag(doc, "citation_date", "2023-09-19")
    assert_tag(doc, "citation_technical_report_number", "TEST-000")
    assert_tag(
        doc, "citation_fulltext_html_url", "https://test-000.example.com/"
    )
    assert_tag(doc, "citation_author", "Jonathan Sick")
    assert_tag(
        doc, "citation_author_orcid", "https://orcid.org/0000-0003-3001-676X"
    )
    assert_tag(doc, "citation_author_institution", "Rubin Observatory")

    # Test for Open Graph metadata tags
    assert_og(doc, "title", "Metadata test document")
    assert_og(
        doc,
        "description",
        "First paragraph of abstract.\n\nSecond paragraph of abstract.",
    )
    assert_og(doc, "url", "https://test-000.example.com/")
    assert_og(doc, "type", "article")
    assert_og(doc, "article:author", "Jonathan Sick")
    assert_og(doc, "article:published_time", "2023-09-19")


def assert_tag(doc: Any, name: str, content: str, index: int = 0) -> None:
    """Compare the content of a meta tag."""
    assert (
        doc.cssselect(f"meta[name='{name}']")[index].get("content") == content
    )


def assert_og(doc: Any, name: str, content: str, index: int = 0) -> None:
    """Assert the content of an Open Graph tag."""
    assert (
        doc.cssselect(f"meta[property='og:{name}']")[index].get("content")
        == content
    )
