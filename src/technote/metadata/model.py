"""The domain model for metadata about a technote."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .zenodo import ZenodoRole

__all__ = [
    "Organization",
    "Person",
    "Contributor",
    "SourceRepository",
    "TechnoteMetadata",
    "TechnoteState",
    "Status",
    "Citation",
    "Link",
    "StructuredName",
]


@dataclass(kw_only=True)
class Organization:
    """The domain model for an organization (e.g. an institution)."""

    name: str
    """The display name of the institution."""

    internal_id: str | None = None
    """A user-specific identifier for an organization."""

    ror: str | None = None
    """The ROR (ror.org) identifier of the institution."""

    address: str | None = None
    """The address of the institution."""

    url: str | None = None
    """The homepage of the institution."""


@dataclass(kw_only=True)
class StructuredName:
    """The domain model for a structured name (e.g. a person's name)."""

    family: str
    """The person's family names (last name in western culture)."""

    given: str
    """The person's given name (first name in western culture)."""

    @property
    def plain_text_name(self) -> str:
        """The name in plain text."""
        return f"{self.given} {self.family}"


@dataclass(kw_only=True)
class Person:
    """The domain model for a person (e.g. an author)."""

    name: StructuredName
    """The name of the person."""

    email: str | None = None
    """The email address of the person."""

    affiliations: list[Organization] = field(default_factory=list)
    """The institutions the person is affiliated with."""

    orcid: str | None = None
    """The ORCiD ID (URL) of the person."""

    internal_id: str | None = None
    """An internal/institutional identifier for a person."""


class Contributor(Person):
    """The domain model for a contributor."""

    role: ZenodoRole | None = None
    """The role of the contributor, using the Zenodo vocabulary."""

    note: str | None = None
    """A note describing the contribution."""


@dataclass(kw_only=True)
class SourceRepository:
    """The domain model for the technote's source code repository."""

    url: str
    """The URL of the source code repository."""

    path: str = ""
    """The base path of the technote relative to the root of the repository."""

    branch: str | None = None
    """The branch of the source code repository."""

    commit: str | None = None
    """The current commit in the source code repository."""


@dataclass(kw_only=True)
class Link:
    """A link to a webpage."""

    url: str
    """The URL of the webpage."""

    title: str | None = None
    """The title of the webpage."""


class TechnoteState(str, Enum):
    """Standardized states for a technote.

    .. mermaid::

       flowchart LR
         draft --> stable
         stable --> draft
         stable --> deprecated
         draft --> deprecated
    """

    draft = "draft"
    """The technote is being actively drafted and updated. It may not be
    complete.
    """

    stable = "stable"
    """The content is considered stable and intended to be complete and
    accurate.
    """

    deprecated = "deprecated"
    """The technote is no longer relevant and accurate, and may have been
    replaced by other documents.
    """

    other = "other"
    """The technote's state is not described by the controlled vocabulary.
    Use the ``TechnoteStatus.note`` field to explain.
    """


@dataclass(kw_only=True)
class Status:
    """The domain model for the technote's content status."""

    state: TechnoteState
    """The state of the technote."""

    note: str | None
    """An explanation of the state."""

    supersceding_urls: list[Link] = field(default_factory=list)
    """URLs to documents/webpages that superscede the technote."""


@dataclass(kw_only=True)
class Citation:
    """Additional information for building a citation to the technote.

    Information such as title, authors, and dates are available in the
    `TechnoteMetadata` model.
    """

    doi: str | None = None
    """The DOI of the technote."""

    ads_bibcode: str | None = None
    """The ADS bibcode of the technote."""


@dataclass(kw_only=True)
class TechnoteMetadata:
    """The domain model for metadata about a technote."""

    title: str
    """The title of the technote."""

    status: Status
    """The status of the technote."""

    canonical_url: str | None = None
    """The canonical URL of the technote."""

    id: str | None = None
    """The institutional identifier for a technote."""

    series_id: str | None = None
    """The identifier for the series the technote belongs to."""

    date_created: datetime | None = None
    """The date when the technote was created."""

    date_updated: datetime | None = None
    """The date when the technote was last updated."""

    version: str | None = None
    """The version of the technote."""

    authors: list[Person] = field(default_factory=list)
    """The authors of the technote."""

    contributors: list[Contributor] = field(default_factory=list)
    """The additional contributors to the technote."""

    source_repository: SourceRepository | None = None
    """The source code repository for the technote."""

    license_id: str | None = None
    """The SPDX license identifier for the technote."""

    citation: Citation | None = None
    """Additional information for citing the technote."""

    abstract_plain: str | None = None
    """The technote's abstract in plain text."""
