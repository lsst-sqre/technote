"""Tests for the technote.ext.toc module."""

from __future__ import annotations

from pathlib import Path
from typing import IO

import lxml.html
import pytest
from sphinx.application import Sphinx
from sphinx.util import logging


@pytest.mark.sphinx("html", testroot="toc-basic")
def test_toc_html(app: Sphinx, status: IO, warning: IO) -> None:
    """Test against the ``test-toc-basic`` test root.

    This test ensures that the technote_toc is rendered into HTML properly.
    """
    app.verbosity = 2
    logging.setup(app, status, warning)
    app.builder.build_all()

    html_source = Path(app.outdir).joinpath("index.html").read_text()
    doc = lxml.html.document_fromstring(html_source)

    toc_ul = doc.cssselect(".technote-toc-container > ul")[0]

    abstract_li = toc_ul.cssselect("li")[0]
    assert abstract_li.text_content() == "Abstract"
    assert abstract_li.cssselect("a")[0].get("href") == "#abstract"

    first_section_li = toc_ul.cssselect("li")[1]
    assert first_section_li.text_content() == "Section one"
    assert first_section_li.cssselect("a")[0].get("href") == "#section-one"
