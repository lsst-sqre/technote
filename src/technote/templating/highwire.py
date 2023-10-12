"""Support for the Hirewire schema for academic metadata HTML in HTML."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .metatagbase import MetaTagFormatterBase

if TYPE_CHECKING:
    from technote.metadata.model import TechnoteMetadata


class HighwireMetadata(MetaTagFormatterBase):
    """A class that transforms technote metadata into Highwire metadata
    tags.

    Notes
    -----
    Resources for learning about Highwire metadata tags:

    - https://cheb.hatenablog.com/entry/2014/07/25/002548#f-c017c3cf
    - https://scholar.google.com/intl/en/scholar/inclusion.html#indexing
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
            "author_info",
            "date",
            "doi",
            "technical_report_number",
            "html_url",
        ]

    @property
    def title(self) -> str:
        """The title metadata."""
        return (
            f'<meta name="citation_title" content="{ self._metadata.title }">'
        )

    @property
    def author_info(self) -> list[str]:
        """The author metadata.

        Each author is represented with these tags:

        - ``citation_author``
        - ``citation_author_institution``
        - ``citation_author_email``
        - ``citation_author_orcid``
        """
        authors = self._metadata.authors
        author_tags: list[str] = []
        for author in authors:
            author_tags.append(
                self._format_tag("author", author.name.plain_text_name)
            )
            affil_tags = [
                self._format_tag("author_institution", affiliation.name)
                for affiliation in author.affiliations
                if affiliation.name is not None
            ]
            author_tags.extend(affil_tags)
            if author.email is not None:
                author_tags.append(
                    self._format_tag("author_email", author.email)
                )
            if author.orcid is not None:
                author_tags.append(
                    self._format_tag("author_orcid", str(author.orcid))
                )
        return author_tags

    @property
    def date(self) -> str | None:
        """The ``citation_date`` metadata tag.

        The format for the date is ``YYYY/MM/DD``. The updated date is used,
        but if that is not available, the created date is used.
        """
        # Use either the date_updated or date_created
        if (
            self._metadata.date_updated is None
            and self._metadata.date_created is None
        ):
            return None
        elif self._metadata.date_updated is not None:
            dt = self._metadata.date_updated
        elif self._metadata.date_created is not None:
            dt = self._metadata.date_created
        else:
            raise RuntimeError(
                "Cannot resolve a date source for citation_date"
            )

        return self._format_tag("date", dt.strftime("%Y/%m/%d"))

    @property
    def doi(self) -> str | None:
        """The ``citation_doi`` metadata tag."""
        if (
            self._metadata.citation is None
            or self._metadata.citation.doi is None
        ):
            return None
        return self._format_tag("doi", str(self._metadata.citation.doi))

    @property
    def technical_report_number(self) -> str | None:
        """The ``citation_technical_report_number`` metadata tag."""
        if self._metadata.id is None:
            return None
        return self._format_tag("technical_report_number", self._metadata.id)

    @property
    def html_url(self) -> str | None:
        """The ``citation_fulltext_html_url`` metadata tag."""
        if self._metadata.canonical_url is None:
            return None
        return self._format_tag(
            "fulltext_html_url", str(self._metadata.canonical_url)
        )

    def _format_tag(self, name: str, content: str) -> str:
        """Format a Highwire metadata tag."""
        return (
            f'<meta name="citation_{ name }" content="{ content }" '
            f'data-highwire="true">'
        )
