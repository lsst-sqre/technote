"""Tests for the technote.templating.dublincore module."""

from __future__ import annotations

from technote.metadata.model import (
    Citation,
    Organization,
    Person,
    Status,
    StructuredName,
    TechnoteMetadata,
    TechnoteState,
)
from technote.templating.dublincore import DublinCoreMetadata


def make_metadata(**kwargs: object) -> TechnoteMetadata:
    """Create a TechnoteMetadata with defaults that tests can override."""
    defaults: dict[str, object] = {
        "title": "Metadata test document",
        "status": Status(state=TechnoteState.stable, note=None),
        "canonical_url": "https://test-000.example.com/",
        "id": "TEST-000",
        "authors": [
            Person(
                name=StructuredName(family="Sick", given="Jonathan"),
                affiliations=[Organization(name="Rubin Observatory")],
            )
        ],
        "abstract_plain": "An abstract.",
    }
    defaults.update(kwargs)
    return TechnoteMetadata(**defaults)  # type: ignore[arg-type]


def test_dublincore_with_doi() -> None:
    """The DOI URL is the DC.identifier when a DOI is available."""
    metadata = make_metadata(
        citation=Citation(doi="10.5281/zenodo.10385500"),
        organization=Organization(name="Vera C. Rubin Observatory"),
        license_id="CC-BY-4.0",
    )
    html = DublinCoreMetadata(metadata=metadata).as_html()

    assert '<meta name="DC.title" content="Metadata test document" >' in html
    assert '<meta name="DC.creator" content="Jonathan Sick" >' in html
    assert (
        '<meta name="DC.identifier" '
        'content="https://doi.org/10.5281/zenodo.10385500" >'
    ) in html
    assert (
        '<meta name="DC.publisher" content="Vera C. Rubin Observatory" >'
        in html
    )
    assert '<meta name="DC.rights" content="CC-BY-4.0" >' in html
    assert '<meta name="DC.description" content="An abstract." >' in html
    assert '<meta name="DC.type" content="Text" >' in html
    assert '<meta name="DC.format" content="text/html" >' in html
    assert '<meta name="DC.language" content="en" >' in html


def test_dublincore_without_doi() -> None:
    """The canonical URL is the DC.identifier fallback without a DOI."""
    html = DublinCoreMetadata(metadata=make_metadata()).as_html()

    assert (
        '<meta name="DC.identifier" '
        'content="https://test-000.example.com/" >'
    ) in html
    assert "doi.org" not in html
    assert "DC.publisher" not in html
    assert "DC.rights" not in html


def test_dublincore_minimal() -> None:
    """Optional tags are omitted when their metadata is unavailable."""
    metadata = TechnoteMetadata(
        title="Bare document",
        status=Status(state=TechnoteState.draft, note=None),
    )
    html = DublinCoreMetadata(metadata=metadata).as_html()

    assert '<meta name="DC.title" content="Bare document" >' in html
    assert "DC.identifier" not in html
    assert "DC.creator" not in html
    assert "DC.description" not in html
    assert "DC.date" not in html


def test_dublincore_escapes_content() -> None:
    """Characters that are markup in HTML are escaped in tag content."""
    metadata = make_metadata(title='A "quoted" & <angled> title')
    html = DublinCoreMetadata(metadata=metadata).as_html()

    assert (
        '<meta name="DC.title" '
        'content="A &quot;quoted&quot; &amp; &lt;angled&gt; title" >'
    ) in html
