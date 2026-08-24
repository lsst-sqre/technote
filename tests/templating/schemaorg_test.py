"""Tests for the technote.templating.schemaorg module."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from technote.metadata.model import (
    Citation,
    Organization,
    Person,
    Status,
    StructuredName,
    TechnoteMetadata,
    TechnoteState,
)
from technote.templating.schemaorg import SchemaDotOrgMetadata


def make_metadata(**kwargs: object) -> TechnoteMetadata:
    """Create a TechnoteMetadata with defaults that tests can override."""
    defaults: dict[str, object] = {
        "title": "Metadata test document",
        "status": Status(state=TechnoteState.stable, note=None),
        "canonical_url": "https://test-000.example.com/",
        "id": "TEST-000",
        "version": "1.0.0",
        "date_created": datetime(2023, 9, 1, tzinfo=UTC),
        "date_updated": datetime(2023, 9, 19, tzinfo=UTC),
        "authors": [
            Person(
                name=StructuredName(family="Sick", given="Jonathan"),
                orcid="https://orcid.org/0000-0003-3001-676X",
                email="jsick@example.com",
                affiliations=[
                    Organization(
                        name="Rubin Observatory",
                        ror="https://ror.org/048g3cy84",
                    )
                ],
            )
        ],
        "abstract_plain": "An abstract.",
    }
    defaults.update(kwargs)
    return TechnoteMetadata(**defaults)  # type: ignore[arg-type]


def test_schemaorg_with_doi() -> None:
    """The DOI is the node identifier when a DOI is available."""
    metadata = make_metadata(
        citation=Citation(doi="10.5281/zenodo.10385500"),
        organization=Organization(
            name="Vera C. Rubin Observatory",
            ror="https://ror.org/048g3cy84",
            url="https://www.lsst.org",
        ),
        license_id="CC-BY-4.0",
    )
    data = SchemaDotOrgMetadata(metadata=metadata).as_json_ld()

    assert data["@context"] == "https://schema.org"
    assert data["@type"] == "Report"
    assert data["@id"] == "https://doi.org/10.5281/zenodo.10385500"
    assert data["url"] == "https://test-000.example.com/"
    assert data["identifier"] == {
        "@type": "PropertyValue",
        "propertyID": "DOI",
        "value": "10.5281/zenodo.10385500",
        "url": "https://doi.org/10.5281/zenodo.10385500",
    }
    assert data["name"] == "Metadata test document"
    assert data["abstract"] == "An abstract."
    assert data["description"] == "An abstract."
    assert data["reportNumber"] == "TEST-000"
    assert data["version"] == "1.0.0"
    assert data["datePublished"] == "2023-09-01"
    assert data["dateModified"] == "2023-09-19"
    assert data["inLanguage"] == "en"
    assert data["license"].startswith(
        "https://creativecommons.org/licenses/by/4.0"
    )

    author = data["author"][0]
    assert author["@type"] == "Person"
    assert author["name"] == "Jonathan Sick"
    assert author["givenName"] == "Jonathan"
    assert author["familyName"] == "Sick"
    assert author["@id"] == "https://orcid.org/0000-0003-3001-676X"
    assert author["email"] == "jsick@example.com"
    assert author["affiliation"] == [
        {
            "@type": "Organization",
            "name": "Rubin Observatory",
            "@id": "https://ror.org/048g3cy84",
        }
    ]

    publisher = data["publisher"]
    assert publisher["name"] == "Vera C. Rubin Observatory"
    assert publisher["@id"] == "https://ror.org/048g3cy84"
    assert publisher["url"] == "https://www.lsst.org"


def test_schemaorg_without_doi() -> None:
    """The canonical URL is the node identifier without a DOI."""
    data = SchemaDotOrgMetadata(metadata=make_metadata()).as_json_ld()

    assert data["@id"] == "https://test-000.example.com/"
    assert "identifier" not in data
    assert "publisher" not in data
    assert "license" not in data


def test_schemaorg_minimal() -> None:
    """Optional keys are omitted when their metadata is unavailable."""
    metadata = TechnoteMetadata(
        title="Bare document",
        status=Status(state=TechnoteState.draft, note=None),
    )
    data = SchemaDotOrgMetadata(metadata=metadata).as_json_ld()

    assert data == {
        "@context": "https://schema.org",
        "@type": "Report",
        "name": "Bare document",
        "inLanguage": "en",
    }


def test_schemaorg_as_html() -> None:
    """The JSON-LD is wrapped in a script tag with markup escaped."""
    metadata = make_metadata(title="A <script> & title")
    html = SchemaDotOrgMetadata(metadata=metadata).as_html()

    assert html.startswith('<script type="application/ld+json">')
    assert html.endswith("</script>")
    # The title's markup characters must not appear literally, otherwise
    # they would end the script element early.
    assert "<script> & title" not in html
    assert "\\u003cscript\\u003e \\u0026 title" in html

    content = html.removeprefix('<script type="application/ld+json">')
    content = content.removesuffix("</script>")
    assert json.loads(content)["name"] == "A <script> & title"


def test_schemaorg_str() -> None:
    """Rendering the class as a string produces the script tag."""
    schemaorg = SchemaDotOrgMetadata(metadata=make_metadata())
    assert str(schemaorg) == schemaorg.as_html()


def test_schemaorg_publisher_without_name() -> None:
    """A publisher identified only by a ROR omits the name entirely."""
    metadata = make_metadata(
        organization=Organization(name="", ror="https://ror.org/048g3cy84")
    )
    data = SchemaDotOrgMetadata(metadata=metadata).as_json_ld()

    assert data["publisher"] == {
        "@type": "Organization",
        "@id": "https://ror.org/048g3cy84",
    }


def test_schemaorg_publisher_without_identity() -> None:
    """A publisher with neither a name nor a public identifier is dropped."""
    metadata = make_metadata(
        organization=Organization(name="", internal_id="rubin")
    )
    data = SchemaDotOrgMetadata(metadata=metadata).as_json_ld()

    assert "publisher" not in data
