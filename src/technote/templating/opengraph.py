"""Support for generating Open Graph metadata tags in HTML."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .metatagbase import MetaTagFormatterBase

if TYPE_CHECKING:
    from technote.metadata.model import TechnoteMetadata


class OpenGraphMetadata(MetaTagFormatterBase):
    """A class that transforms technote metadata into Open Graph metadata.

    Notes
    -----
    Resources for learning about Open Graph metadata tags:

    - https://ogp.me/
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
            "description",
            "url",
            "og_type",
            "authors",
            "dates",
        ]

    @property
    def title(self) -> str:
        """The title of the technote."""
        return self._format_tag("title", self._metadata.title)

    @property
    def description(self) -> str | None:
        """The abstract of the technote."""
        if self._metadata.abstract_plain is None:
            return None
        return self._format_tag("description", self._metadata.abstract_plain)

    @property
    def url(self) -> str | None:
        """The canonical HTML URL of the technote."""
        if self._metadata.canonical_url is None:
            return None
        return self._format_tag("url", str(self._metadata.canonical_url))

    @property
    def og_type(self) -> str | None:
        """The OpenGraph type of the technote."""
        return self._format_tag("type", "article")

    @property
    def authors(self) -> list[str]:
        """The article authors."""
        authors = self._metadata.authors
        return [
            self._format_tag("article:author", author.name.plain_text_name)
            for author in authors
        ]

    @property
    def dates(self) -> list[str]:
        """The `article:published_time` and `article:modified_time` tags.

        When only one of `TechnoteTable.date_created` or
        `TechnoteTable.date_updated` are available, that date is used as the
        `article:published_time` and `article:modified_time` is not set.
        """
        if (
            self._metadata.date_created is None
            and self._metadata.date_updated is not None
        ):
            return [
                self._format_tag(
                    "article:published_time",
                    self._format_datetime(self._metadata.date_updated),
                )
            ]
        if (
            self._metadata.date_updated is None
            and self._metadata.date_created is not None
        ):
            return [
                self._format_tag(
                    "article:published_time",
                    self._format_datetime(self._metadata.date_created),
                )
            ]
        if (
            self._metadata.date_updated is not None
            and self._metadata.date_created is not None
        ):
            return [
                self._format_tag(
                    "article:published_time",
                    self._format_datetime(self._metadata.date_created),
                ),
                self._format_tag(
                    "article:modified_time",
                    self._format_datetime(self._metadata.date_updated),
                ),
            ]
        return []

    def _format_datetime(self, dt: datetime) -> str:
        """Format a datetime object as an ISO 8601 string."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        dt = dt.astimezone(UTC)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _format_tag(self, name: str, content: str) -> str:
        """Format a OpenGraph metadata tag."""
        return f'<meta property="og:{ name }" content="{ content }" >'
