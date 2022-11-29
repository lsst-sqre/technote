"""Tests for the technote.ext.abstract module."""

from __future__ import annotations

from pathlib import Path
from typing import IO

import lxml.html
import pytest
from sphinx.application import Sphinx
from sphinx.util import logging


@pytest.mark.sphinx("html", testroot="abstract-basic")
def test_abstract_basic_html(app: Sphinx, status: IO, warning: IO) -> None:
    """Test against the ``test-abstract-basic`` test root.

    This test ensures that the abstract is rendered in HTML with a
    wrapper section and a h2.
    """
    app.verbosity = 2
    logging.setup(app, status, warning)
    app.builder.build_all()

    html_source = Path(app.outdir).joinpath("index.html").read_text()
    doc = lxml.html.document_fromstring(html_source)

    section = doc.cssselect("section.technote-abstract")[0]
    assert section.get("id") == "abstract"

    heading = section.cssselect("h2")[0]
    assert heading.text_content() == "Abstract"
    assert "technote-abstract__header" in heading.classes

    first_para = section.cssselect("p")[0]
    assert first_para.text_content().startswith("First paragraph of abstract.")

    second_para = section.cssselect("p")[1]
    assert second_para.text_content().startswith(
        "Second paragraph of abstract."
    )
