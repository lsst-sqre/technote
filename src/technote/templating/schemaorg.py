"""Support for generating schema.org JSON-LD metadata in HTML."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from ..metadata.spdx import load_licenses
from .dateformat import format_iso_date

if TYPE_CHECKING:
    from technote.metadata.model import Organization, Person, TechnoteMetadata

__all__ = ["SchemaDotOrgMetadata"]


class SchemaDotOrgMetadata:
    """A class that transforms technote metadata into a schema.org JSON-LD
    block.

    Notes
    -----
    The technote is described as a schema.org ``Report``. When the technote
    has a DOI, the DOI URL is the node identifier (``@id``) and the DOI is
    also expressed as a ``PropertyValue`` identifier, following the
    DataCite-to-schema.org crosswalk. This makes the technote's HTML page a
    well-formed DOI landing page.

    Resources for learning about schema.org JSON-LD:

    - https://schema.org/Report
    - https://json-ld.org/
    - https://github.com/datacite/schema/blob/master/source/meta/kernel-4/include/datacite-schemaOrg-v4.xsd
    """

    def __init__(
        self,
        *,
        metadata: TechnoteMetadata,
    ) -> None:
        self._metadata = metadata

    def __str__(self) -> str:
        """Create the JSON-LD ``script`` tag."""
        return self.as_html()

    def as_json_ld(self) -> dict[str, Any]:
        """Create the JSON-LD document as a Python dictionary."""
        data: dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Report",
            "name": self._metadata.title,
        }
        data.update(self._identity_fields())
        data.update(self._description_fields())
        data.update(self._date_fields())
        data.update(self._attribution_fields())
        data["inLanguage"] = "en"
        return data

    def as_html(self) -> str:
        """Create the JSON-LD metadata as an HTML ``script`` tag."""
        content = json.dumps(self.as_json_ld(), indent=2)
        return (
            '<script type="application/ld+json">\n'
            f"{self._escape_json(content)}\n"
            "</script>"
        )

    def _identity_fields(self) -> dict[str, Any]:
        """Build the fields that identify and locate the technote."""
        data: dict[str, Any] = {}

        citation = self._metadata.citation
        doi_url = citation.doi_url if citation is not None else None
        canonical_url = self._metadata.canonical_url

        if doi_url is not None:
            data["@id"] = doi_url
        elif canonical_url is not None:
            data["@id"] = str(canonical_url)

        if canonical_url is not None:
            data["url"] = str(canonical_url)

        if citation is not None and citation.doi is not None:
            data["identifier"] = {
                "@type": "PropertyValue",
                "propertyID": "DOI",
                "value": citation.doi,
                "url": doi_url,
            }

        return data

    def _description_fields(self) -> dict[str, Any]:
        """Build the fields that describe the technote's content."""
        data: dict[str, Any] = {}
        if self._metadata.abstract_plain is not None:
            data["abstract"] = self._metadata.abstract_plain
            data["description"] = self._metadata.abstract_plain
        if self._metadata.id is not None:
            data["reportNumber"] = self._metadata.id
        if self._metadata.version is not None:
            data["version"] = self._metadata.version
        return data

    def _date_fields(self) -> dict[str, Any]:
        """Build the publication and modification date fields."""
        data: dict[str, Any] = {}
        if self._metadata.date_created is not None:
            data["datePublished"] = format_iso_date(
                self._metadata.date_created
            )
        if self._metadata.date_updated is not None:
            data["dateModified"] = format_iso_date(self._metadata.date_updated)
        return data

    def _attribution_fields(self) -> dict[str, Any]:
        """Build the author, publisher, and license fields."""
        data: dict[str, Any] = {}

        authors = [
            self._format_person(author) for author in self._metadata.authors
        ]
        if authors:
            data["author"] = authors

        organization = self._metadata.organization
        if organization is not None and (
            organization.name or organization.ror or organization.url
        ):
            # An organization with only an internal ID can't be described
            # to a schema.org consumer, so it's dropped entirely.
            data["publisher"] = self._format_organization(organization)

        license_url = self._license_url
        if license_url is not None:
            data["license"] = license_url

        return data

    @property
    def _license_url(self) -> str | None:
        """The URL of the license, resolved from the SPDX license ID."""
        license_id = self._metadata.license_id
        if license_id is None:
            return None
        licenses = load_licenses()
        if license_id not in licenses:
            return None
        see_also = licenses[license_id].see_also
        if not see_also:
            return None
        return str(see_also[0])

    def _format_person(self, person: Person) -> dict[str, Any]:
        """Format a `~technote.metadata.model.Person` as a schema.org
        ``Person``.
        """
        data: dict[str, Any] = {
            "@type": "Person",
            "name": person.name.plain_text_name,
            "givenName": person.name.given,
            "familyName": person.name.family,
        }
        if person.orcid is not None:
            data["@id"] = str(person.orcid)
        if person.email is not None:
            data["email"] = person.email
        affiliations = [
            self._format_organization(affiliation)
            for affiliation in person.affiliations
            if affiliation.name
        ]
        if affiliations:
            data["affiliation"] = affiliations
        return data

    def _format_organization(
        self, organization: Organization
    ) -> dict[str, Any]:
        """Format an `~technote.metadata.model.Organization` as a schema.org
        ``Organization``.
        """
        data: dict[str, Any] = {"@type": "Organization"}
        if organization.name:
            data["name"] = organization.name
        if organization.ror is not None:
            data["@id"] = str(organization.ror)
        if organization.url is not None:
            data["url"] = str(organization.url)
        if organization.address is not None:
            data["address"] = organization.address
        return data

    @staticmethod
    def _escape_json(content: str) -> str:
        """Escape characters that would otherwise end the ``script`` element
        early, or be interpreted as HTML markup.
        """
        return (
            content.replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
        )
