"""Test the representation of metadata in the generated site."""

from __future__ import annotations

from pathlib import Path
from typing import IO, Any

import lxml.html
import mf2py
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
    assert_tag(doc, "citation_date", "2023/09/19")
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
    assert_og(doc, "article:published_time", "2023-09-19T00:00:00Z")

    # Find technote data attributes
    source_link = doc.cssselect("[data-technote-source-url]")[0]
    assert (
        source_link.get("data-technote-source-url")
        == "https://github.com/lsst-sqre/sqr-000"
    )

    # Find standard HTML metadata
    assert doc.cssselect("title")[0].text == "Metadata test document"
    assert (
        doc.cssselect("meta[name='description']")[0].get("content")
        == "First paragraph of abstract.\n\nSecond paragraph of abstract."
    )
    assert (
        doc.cssselect("link[rel='canonical']")[0].get("href")
        == "https://test-000.example.com/"
    )
    found_technote_generator = False
    for tag in doc.cssselect("meta[name='generator']"):
        if tag.get("content").split(" ")[0] == "technote":
            found_technote_generator = True
    assert found_technote_generator

    # Test for microformats2 metadata
    mf2_parser = mf2py.Parser(doc=html_source)
    mf2_data = mf2_parser.to_dict()
    detected_hentry = False
    for h_item in mf2_data["items"]:
        if "h-entry" in h_item["type"]:
            detected_hentry = True
            props = h_item["properties"]
            # The post-build cleanup doesn't run with the test builder,
            # so the insertposttitle extension doesn't run; hence inline
            # author info won't be added.
            assert props["updated"][0] == "2023-09-19T00:00:00Z"
            assert "content" in props
            assert "summary" in props
    assert detected_hentry


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
