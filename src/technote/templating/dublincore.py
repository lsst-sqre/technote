"""Support for generating Dublin Core metadata tags in HTML."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .dateformat import format_iso_date
from .metatagbase import MetaTagFormatterBase

if TYPE_CHECKING:
    from technote.metadata.model import TechnoteMetadata

__all__ = ["DublinCoreMetadata"]


class DublinCoreMetadata(MetaTagFormatterBase):
    """A class that transforms technote metadata into Dublin Core metadata
    tags.

    Notes
    -----
    Dublin Core is a general-purpose bibliographic vocabulary used by
    repository software and harvesters. The ``DC.identifier`` tag in
    particular is how a landing page declares the persistent identifier
    (the DOI) of the resource it describes.

    Resources for learning about Dublin Core metadata tags:

    - https://www.dublincore.org/specifications/dublin-core/dces/
    - https://www.dublincore.org/specifications/dublin-core/dc-html/
    """

    def __init__(
        self,
        *,
        metadata: TechnoteMetadata,
    ) -> None:
        self._metadata = metadata

    @property
    def tag_attributes(self) -> list[str]:
        """The names of class properties that create tags."""
        return [
            "title",
            "creators",
            "description",
            "identifier",
            "date",
            "publisher",
            "dc_type",
            "dc_format",
            "language",
            "rights",
        ]

    @property
    def title(self) -> str:
        """The ``DC.title`` metadata tag."""
        return self._format_tag("title", self._metadata.title)

    @property
    def creators(self) -> list[str]:
        """The ``DC.creator`` metadata tag for each author."""
        return [
            self._format_tag("creator", author.name.plain_text_name)
            for author in self._metadata.authors
        ]

    @property
    def description(self) -> str | None:
        """The ``DC.description`` metadata tag, from the abstract."""
        if self._metadata.abstract_plain is None:
            return None
        return self._format_tag("description", self._metadata.abstract_plain)

    @property
    def identifier(self) -> str | None:
        """The ``DC.identifier`` metadata tag.

        The DOI (as a ``https://doi.org`` URL) is preferred because it is the
        persistent identifier for the technote. The canonical URL is used as
        a fallback when the technote does not have a DOI.
        """
        if (
            self._metadata.citation is not None
            and self._metadata.citation.doi_url is not None
        ):
            return self._format_tag(
                "identifier", self._metadata.citation.doi_url
            )
        if self._metadata.canonical_url is not None:
            return self._format_tag(
                "identifier", str(self._metadata.canonical_url)
            )
        return None

    @property
    def date(self) -> str | None:
        """The ``DC.date`` metadata tag (``YYYY-MM-DD``, in UTC).

        The creation date is the date of publication. The updated date is
        used when a creation date is not available.
        """
        dt = self._metadata.date_created or self._metadata.date_updated
        if dt is None:
            return None
        return self._format_tag("date", format_iso_date(dt))

    @property
    def publisher(self) -> str | None:
        """The ``DC.publisher`` metadata tag, from the organization."""
        if self._metadata.organization is None:
            return None
        if not self._metadata.organization.name:
            return None
        return self._format_tag("publisher", self._metadata.organization.name)

    @property
    def dc_type(self) -> str:
        """The ``DC.type`` metadata tag."""
        return self._format_tag("type", "Text")

    @property
    def dc_format(self) -> str:
        """The ``DC.format`` metadata tag."""
        return self._format_tag("format", "text/html")

    @property
    def language(self) -> str:
        """The ``DC.language`` metadata tag."""
        return self._format_tag("language", "en")

    @property
    def rights(self) -> str | None:
        """The ``DC.rights`` metadata tag, from the SPDX license ID."""
        if self._metadata.license_id is None:
            return None
        return self._format_tag("rights", self._metadata.license_id)

    def _format_tag(self, name: str, content: str) -> str:
        """Format a Dublin Core metadata tag."""
        escaped = self.escape_content(content)
        return f'<meta name="DC.{ name }" content="{ escaped }" >'
