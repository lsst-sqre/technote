"""The Jinja context for Sphinx HTML templates."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.parse import urlparse

from ..metadata.model import TechnoteMetadata
from .highwire import HighwireMetadata
from .opengraph import OpenGraphMetadata


class TechnoteJinjaContext:
    """A class available to the Jinja context in HTML templates and
    provides access to technote metadata.

    Parameters
    ----------
    metadata
        The technote metadata.
    """

    def __init__(
        self, metadata: TechnoteMetadata, root_filename: Path
    ) -> None:
        self._metadata = metadata
        self._root_filename = root_filename

    @property
    def metadata(self) -> TechnoteMetadata:
        """The technote metadata."""
        return self._metadata

    @property
    def title(self) -> str:
        """The technote's title.

        This title can be derived either from the top-level header in the
        document ``title`` field in ``technote.toml`` if set.
        """
        return self.metadata.title

    @property
    def abstract(self) -> str | None:
        """The technote's unformatted abstract.

        This content is extracted from the ``abstract`` directive, and all
        markup is removed as part of that process. This attribute can be used
        for populating summary tags in the HTML header.
        """
        return self.metadata.abstract_plain

    @property
    def date_updated_iso(self) -> str | None:
        """The date updated, as an ISO 8601 string (YYYY-MM-DD)."""
        if self.metadata.date_updated:
            return self._format_iso_date(self.metadata.date_updated)
        else:
            return None

    @property
    def date_created_iso(self) -> str | None:
        """The date of initial publication, as ISO 8601 (YYYY-MM-DD)."""
        if self.metadata.date_created:
            return self._format_iso_date(self.metadata.date_created)
        else:
            return None

    @property
    def datetime_updated_iso(self) -> str | None:
        """The datetime updated, as an ISO 8601 string normalized to UTC."""
        if self.metadata.date_updated:
            return self._format_iso_datetime(self.metadata.date_updated)
        else:
            return None

    @property
    def datetime_created_iso(self) -> str | None:
        """The datetime of initial publication, as an ISO 8601 string
        normalized to UTC.
        """
        if self.metadata.date_created:
            return self._format_iso_datetime(self.metadata.date_created)
        else:
            return None

    @property
    def version(self) -> str | None:
        """The version, as a string if available."""
        return self.metadata.version

    @property
    def canonical_url(self) -> str | None:
        """The canonical URL of the technote, if available."""
        return str(self.metadata.canonical_url)

    @property
    def github_url(self) -> str | None:
        """The GitHub repository URL."""
        if (
            self.metadata.source_repository is not None
            and self.metadata.source_repository.url is not None
            and self.metadata.source_repository.url.startswith(
                "https://github.com"
            )
        ):
            return str(self.metadata.source_repository.url)
        return None

    @property
    def github_repo_slug(self) -> str | None:
        """The GitHub repository slug, ``owner/name``."""
        if self.github_url is None:
            return None

        url_parts = urlparse(self.github_url)
        slug = "/".join(url_parts.path.lstrip("/").split("/")[:2])
        return slug.removesuffix(".git")

    @property
    def github_ref_name(self) -> str | None:
        """The branch or tag name."""
        # FIXME: this is calculated from GitHub Actions environment variables
        # https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables
        return os.getenv("GITHUB_REF_NAME")

    @property
    def github_ref_type(self) -> str | None:
        """The ref type: branch or tag."""
        # FIXME: this is calculated from GitHub Actions environment variables
        # https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables
        return os.getenv("GITHUB_REF_TYPE")

    @property
    def github_edit_url(self) -> str | None:
        """The URL for editing content on GitHub, from its default branch."""
        if self.github_url is None:
            return None
        if self.metadata.source_repository is None:
            return None

        if self.github_url.endswith(".git"):  # replace with str.removesuffix
            root_url = self.github_url[:-4]
        else:
            root_url = self.github_url

        filename = self._root_filename.name

        # We're using /blob/ instead of /edit/ to give users the choice of
        # how to edit (on web or in github.dev).
        return (
            f"{root_url}/blob/"
            f"{self.metadata.source_repository.branch or 'main'}/{filename}"
        )

    def set_content_title(self, title: str) -> None:
        """Set the title from the content nodes."""
        # If the title is empty, that indicates that it was not set in
        # technote.toml. We can set it from the content. But if it was set
        # we don't want to override that choice.
        if self.metadata.title == "":
            self.metadata.title = title

    def set_abstract(self, abstract: str) -> None:
        """Set the abstract metadata from the content."""
        self.metadata.abstract_plain = abstract

    def _format_iso_datetime(self, date: datetime) -> str:
        """Format a date in ISO 8601 format, normalized to UTC."""
        dt = date.astimezone(UTC)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _format_iso_date(self, date: datetime) -> str:
        """Format a date in ISO 8601 date format, normalized to UTC."""
        dt = date.astimezone(UTC)
        return dt.strftime("%Y-%m-%d")

    @property
    def highwire_metadata_tags(self) -> str:
        """The Highwire metadata tags for the technote."""
        highwire = HighwireMetadata(
            metadata=self.metadata,
        )
        return highwire.as_html()

    @property
    def opengraph_metadata_tags(self) -> str:
        """The OpenGraph metadata tags for the technote."""
        og = OpenGraphMetadata(
            metadata=self.metadata,
        )
        return og.as_html()

    @property
    def generator_tag(self) -> str:
        """A meta name=generator tag to identify the version of technote."""
        try:
            tn_version = version("technote")
        except PackageNotFoundError:
            # package is not installed
            tn_version = "0.0.0"
        return (
            f'<meta name="generator" content="technote {tn_version}: '
            'https://technote.lsst.io" >'
        )
