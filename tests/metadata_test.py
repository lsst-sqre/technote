"""Test the representation of metadata in the generated site."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import IO, Any

import lxml.html
import mf2py
import pytest
from sphinx.application import Sphinx
from sphinx.testing.util import SphinxTestApp
from sphinx.util import logging

from tests.metadata.builddate_test import git


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
    assert_tag(doc, "citation_publication_date", "2023/09/19")
    assert_tag(doc, "citation_technical_report_number", "TEST-000")
    assert_tag(
        doc, "citation_fulltext_html_url", "https://test-000.example.com/"
    )
    assert_tag(doc, "citation_author", "Jonathan Sick")
    assert_tag(
        doc, "citation_author_orcid", "https://orcid.org/0000-0003-3001-676X"
    )
    assert_tag(doc, "citation_author_institution", "Rubin Observatory")
    assert_tag(doc, "citation_doi", "10.5281/zenodo.10385500")

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

    # Test for Dublin Core metadata tags
    assert_tag(doc, "DC.title", "Metadata test document")
    assert_tag(doc, "DC.creator", "Jonathan Sick")
    assert_tag(doc, "DC.identifier", "https://doi.org/10.5281/zenodo.10385500")
    assert_tag(doc, "DC.date", "2023-09-19")
    assert_tag(doc, "DC.publisher", "Vera C. Rubin Observatory")
    assert_tag(doc, "DC.type", "Text")
    assert_tag(doc, "DC.format", "text/html")
    assert_tag(doc, "DC.language", "en")
    assert_tag(doc, "DC.rights", "CC-BY-4.0")
    assert_tag(
        doc,
        "DC.description",
        "First paragraph of abstract.\n\nSecond paragraph of abstract.",
    )

    # Test for the schema.org JSON-LD block
    json_ld_tags = doc.cssselect("script[type='application/ld+json']")
    assert len(json_ld_tags) == 1
    json_ld = json.loads(json_ld_tags[0].text_content())
    assert json_ld["@context"] == "https://schema.org"
    assert json_ld["@type"] == "Report"
    assert json_ld["@id"] == "https://doi.org/10.5281/zenodo.10385500"
    assert json_ld["name"] == "Metadata test document"
    assert json_ld["url"] == "https://test-000.example.com/"
    assert json_ld["identifier"] == {
        "@type": "PropertyValue",
        "propertyID": "DOI",
        "value": "10.5281/zenodo.10385500",
        "url": "https://doi.org/10.5281/zenodo.10385500",
    }
    assert json_ld["reportNumber"] == "TEST-000"
    assert json_ld["version"] == "1.0.0"
    assert json_ld["dateModified"] == "2023-09-19"
    assert json_ld["author"][0]["name"] == "Jonathan Sick"
    assert json_ld["author"][0]["@id"] == (
        "https://orcid.org/0000-0003-3001-676X"
    )
    assert json_ld["author"][0]["affiliation"][0]["name"] == (
        "Rubin Observatory"
    )
    assert json_ld["publisher"]["name"] == "Vera C. Rubin Observatory"
    assert json_ld["license"].startswith(
        "https://creativecommons.org/licenses/by/4.0"
    )
    assert json_ld["inLanguage"] == "en"

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


@pytest.mark.sphinx("html", testroot="abstract-basic")
def test_metadata_without_canonical_url(
    app: Sphinx, status: IO, warning: IO
) -> None:
    """Test that no canonical link is emitted when the technote doesn't
    configure a ``canonical_url``.
    """
    app.verbosity = 2
    logging.setup(app, status, warning)
    app.builder.build_all()

    html_source = Path(app.outdir).joinpath("index.html").read_text()
    doc = lxml.html.document_fromstring(html_source)

    assert doc.cssselect("link[rel='canonical']") == []


@pytest.mark.sphinx("html", testroot="date-updated-default")
def test_metadata_date_updated_default(
    app: Sphinx, status: IO, warning: IO
) -> None:
    """Test that an undeclared ``date_updated`` is pinned to the publication
    date rather than the build clock, and that every metadata surface agrees
    on it.

    The session-wide ``_pin_source_date_epoch`` fixture in ``conftest.py``
    sets ``SOURCE_DATE_EPOCH``, so this exercises the first derived step of
    the resolution order. ``test_metadata_date_updated_from_git`` covers the
    git commit date behind it.
    """
    app.verbosity = 2
    logging.setup(app, status, warning)
    app.builder.build_all()

    html_source = Path(app.outdir).joinpath("index.html").read_text()
    doc = lxml.html.document_fromstring(html_source)

    # SOURCE_DATE_EPOCH=1700000000 is 2023-11-14T22:13:20Z
    assert_tag(doc, "citation_publication_date", "2023/11/14")
    assert_og(doc, "article:published_time", "2023-09-19T00:00:00Z")
    assert_og(doc, "article:modified_time", "2023-11-14T22:13:20Z")

    json_ld_tags = doc.cssselect("script[type='application/ld+json']")
    json_ld = json.loads(json_ld_tags[0].text_content())
    assert json_ld["dateModified"] == "2023-11-14"

    mf2_data = mf2py.Parser(doc=html_source).to_dict()
    h_entries = [h for h in mf2_data["items"] if "h-entry" in h["type"]]
    assert len(h_entries) == 1
    assert h_entries[0]["properties"]["updated"][0] == "2023-11-14T22:13:20Z"


GIT_COMMIT_DATE = "2024-03-05T14:15:16+02:00"
"""Committer date of the test repository built by
``test_metadata_date_updated_from_git``, in UTC+2.
"""

GIT_COMMIT_DATE_UTC = "2024-03-05T12:15:16Z"
"""``GIT_COMMIT_DATE`` in UTC, which is how technote renders it.

It follows the ``date_created`` of the ``date-updated-default`` test root
(2023-09-19), so the clamp to ``date_created`` does not apply.
"""


def test_metadata_date_updated_from_git(
    rootdir: Path,
    tmp_path: Path,
    make_app: Callable[..., SphinxTestApp],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that an undeclared ``date_updated`` defaults to the committer date
    of the checked-out commit.

    This is the shipped default for a technote published by CI, so it is
    exercised end to end: a real git repository, a real Sphinx build, and the
    rendered HTML. Sphinx evaluates ``conf.py`` with the working directory set
    to the configuration directory, which is the assumption that lets the
    factory pass ``Path.cwd()`` as the technote's source directory.
    """
    # Take the git branch of the resolution order rather than the
    # SOURCE_DATE_EPOCH pinned for the session in conftest.py.
    monkeypatch.delenv("SOURCE_DATE_EPOCH")

    srcdir = tmp_path / "technote"
    shutil.copytree(rootdir / "test-date-updated-default", srcdir)
    git("init", "-q", cwd=srcdir, date=GIT_COMMIT_DATE)
    git("add", "-A", cwd=srcdir, date=GIT_COMMIT_DATE)
    git(
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-q",
        "-m",
        "Initial commit",
        cwd=srcdir,
        date=GIT_COMMIT_DATE,
    )

    app = make_app("html", srcdir=srcdir)
    app.build()

    # Failing to read the commit date of a repository that has one warns
    # before falling back to the build clock, so a clean warning stream
    # confirms that the git path succeeded.
    assert "date_updated" not in app.warning.getvalue()

    html_source = Path(app.outdir).joinpath("index.html").read_text()
    doc = lxml.html.document_fromstring(html_source)

    assert_tag(doc, "citation_publication_date", "2024/03/05")
    assert_og(doc, "article:modified_time", GIT_COMMIT_DATE_UTC)

    json_ld_tags = doc.cssselect("script[type='application/ld+json']")
    json_ld = json.loads(json_ld_tags[0].text_content())
    assert json_ld["dateModified"] == "2024-03-05"

    mf2_data = mf2py.Parser(doc=html_source).to_dict()
    h_entries = [h for h in mf2_data["items"] if "h-entry" in h["type"]]
    assert len(h_entries) == 1
    assert h_entries[0]["properties"]["updated"][0] == GIT_COMMIT_DATE_UTC


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
