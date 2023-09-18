"""Support for the Hirewire schema for academic metadata HTML in HTML."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from technote.config import TechnoteTable


class HighwireMetadata:
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
        metadata: TechnoteTable,
        title: str,
        abstract: str | None = None,
    ) -> None:
        self._metadata = metadata
        self._title = title
        self._abstract = abstract

    def __str__(self) -> str:
        """Create the Highwire metadata tags."""
        return self.as_html()

    def as_html(self) -> str:
        """Create the Highwire metadata HTML tags."""
        tags: list[str] = []
        self.extend_not_none(tags, self.title)
        self.extend_not_none(tags, self.author_info)
        self.extend_not_none(tags, self.date)
        self.extend_not_none(tags, self.doi)
        self.extend_not_none(tags, self.technical_report_number)
        self.extend_not_none(tags, self.html_url)
        return "\n".join(tags) + "\n"

    @staticmethod
    def extend_not_none(
        entries: list[str], new_item: None | str | list[str]
    ) -> None:
        """Extend a list with new items if they are not None."""
        if new_item is None:
            return
        if isinstance(new_item, str):
            entries.append(new_item)
        else:
            entries.extend(new_item)

    @property
    def title(self) -> str:
        """The title metadata."""
        return f'<meta name="citation_title" content="{ self._title }">'

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
        """The ``citation_date`` metadata tag."""
        if self._metadata.date_updated is None:
            return None
        iso8601_date = self._metadata.date_updated.isoformat()
        return self._format_tag("date", iso8601_date)

    @property
    def doi(self) -> str | None:
        """The ``citation_doi`` metadata tag."""
        if self._metadata.doi is None:
            return None
        return self._format_tag("doi", str(self._metadata.doi))

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
