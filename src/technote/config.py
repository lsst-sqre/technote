"""Technote configuration models (for technote.toml).

technote.toml is used both for setting document metadata and also configuring
the Sphinx build. Users of Technote can also add tables to technote.toml
to support their technote plugins and build infrastructure.
"""

# Design note
#
# Keep in mind that technote.toml is a configuration file, not a metadata
# export schema. Some metadata can be discovered from the content, and
# reformatted from data in technote.toml (for example, a ORCiD can stand
# in for an author's name, and a ROR can stand in for the name of an
# affiliation.)

from __future__ import annotations

import os
import re
import tomllib
from collections.abc import MutableMapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Self
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    HttpUrl,
    ValidationError,
    field_validator,
    model_validator,
)
from sphinx.errors import ConfigError

from .metadata.highwire import HighwireMetadata
from .metadata.opengraph import OpenGraphMetadata
from .metadata.orcid import validate_orcid_url
from .metadata.orcid import verify_checksum as verify_orcid_checksum
from .metadata.ror import validate_ror_url
from .metadata.spdx import Licenses
from .metadata.zenodo import ZenodoRole

__all__ = [
    "TechnoteToml",
    "TechnoteTable",
    "LicenseTable",
    "TechnoteStatus",
    "TechnoteState",
    "Organization",
    "PersonName",
    "Person",
    "Contributor",
    "SphinxTable",
    "IntersphinxTable",
    "LinkcheckTable",
    "TechnoteSphinxConfig",
    "TechnoteJinjaContext",
]


WHITESPACE_PATTERN = re.compile(r"\s+")


def collapse_whitespace(text: str) -> str:
    """Replace any whitespace character, or group, with a single space."""
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def normalize_datetime(v: Any) -> datetime | None:
    """Pydantic field validator for datetime fields.

    Parameters
    ----------
    v
        Field representing a `~datetime.datetime`.

    Returns
    -------
    datetime.datetime or None
        The timezone-aware `~datetime.datetime` or `None` if the input was
        `None`.

    Examples
    --------
    Here is a partial model that uses this function as a field validator.

    .. code-block:: python

       class Info(BaseModel):
           last_used: datetime | None = Field(
               None,
               title="Last used",
               description="When last used in seconds since epoch",
               examples=[1614986130],
           )

           _normalize_last_used = field_validator("last_used", mode="before")(
               normalize_datetime
           )
    """
    if v is None:
        return v
    if isinstance(v, str):
        dt = datetime.fromisoformat(v)
        if dt.tzinfo and dt.tzinfo.utcoffset(dt) is not None:
            return dt.astimezone(UTC)
        else:
            return dt.replace(tzinfo=UTC)
    if isinstance(v, datetime):
        if v.tzinfo and v.tzinfo.utcoffset(v) is not None:
            return v.astimezone(UTC)
        else:
            return v.replace(tzinfo=UTC)
    raise ValueError("Cannot parse datetime from value: ", v)


class IntersphinxTable(BaseModel):
    """Intersphinx configuration in the ``[technote.sphinx]`` table."""

    projects: dict[str, HttpUrl] = Field(
        description="Mapping of projects and their URLs.", default_factory=dict
    )


class LinkcheckTable(BaseModel):
    """Linkcheck builder configurations in the ``[technote.sphinx]`` table."""

    ignore: list[str] = Field(
        description="Regular expressions of URLs to skip checking links",
        default_factory=list,
    )


class SphinxTable(BaseModel):
    """The ``[technote.sphinx]`` table permits Sphinx project configuration."""

    nitpicky: bool = Field(
        False, description="Escalate warnings to build errors."
    )

    nitpick_ignore: list[tuple[str, str]] = Field(
        description=(
            "Errors to ignore. First item is the type (like a role or "
            "directive) and the second is the target (like the argument to "
            "the role)."
        ),
        default_factory=list,
    )

    nitpick_ignore_regex: list[tuple[str, str]] = Field(
        description=(
            "Same as ``nitpick_ignore``, but both type and target are "
            "interpreted as regular expressions."
        ),
        default_factory=list,
    )

    extensions: list[str] = Field(
        default_factory=list,
        description="Additional Sphinx extensions to use in the build.",
    )

    intersphinx: IntersphinxTable = Field(
        default_factory=IntersphinxTable,
        description="Intersphinx configurations.",
    )

    linkcheck: LinkcheckTable = Field(
        default_factory=LinkcheckTable,
        description="Link check builder settings.",
    )


class Organization(BaseModel):
    """Model for describing an organization (often as an affiliation)."""

    internal_id: str | None = Field(
        None, description="A user-specific identifier for an organization."
    )

    ror: HttpUrl | None = Field(
        None, description="The ROR (ror.org) identifier of the institution."
    )

    name: str | None = Field(
        None, description="The display name of the institution."
    )

    address: str | None = Field(
        None, description="The address of the institution."
    )

    url: HttpUrl | None = Field(
        None, description="The homepage of the institution."
    )

    @field_validator("name")
    @classmethod
    def clean_whitespace(cls, v: str | None) -> str | None:
        if v:
            return collapse_whitespace(v)
        else:
            return v

    @model_validator(mode="after")
    def check_well_defined(self) -> Self:
        """Ensure that at least the internal ID, ROR, or name are provided."""
        if self.internal_id:
            return self
        if self.ror:
            return self
        if self.name:
            return self

        raise ValueError(
            "An organization must have a name, ror, or internal_id"
        )

    @field_validator("ror", mode="after")
    @classmethod
    def validate_ror(cls, v: HttpUrl | None) -> HttpUrl | None:
        """Ensure that ``ror`` is a valid ROR identifier."""
        if v is not None:
            validate_ror_url(v)
        return v


class PersonName(BaseModel):
    """A person's name."""

    family_names: str | None = Field(
        None,
        description="The person's family name (last name in western culture).",
    )

    given_names: str | None = Field(
        None,
        description="The person's given name (first name in western culture).",
    )

    name: str | None = Field(
        None,
        description=(
            "The person's name, an alternative to specifying surname and "
            "given names."
        ),
    )

    @property
    def plain_text_name(self) -> str:
        """The name in plain text."""
        if self.name is not None:
            return self.name
        else:
            return f"{self.given_names} {self.family_names}"

    @field_validator("family_names", "given_names", "name")
    @classmethod
    def clean_whitespace(cls, v: str | None) -> str | None:
        if v:
            return collapse_whitespace(v)
        else:
            return v

    @model_validator(mode="after")
    def check_well_defined(self) -> Self:
        """Check that either surname and given are both provided, or name
        alone is set.
        """
        if self.family_names and self.given_names:
            if self.name:
                raise ValueError(
                    "Do not specify name if family_names and given_names are "
                    "both provided."
                )
            return self

        if self.name:
            if self.family_names:
                raise ValueError(
                    "Do not specify `family_names` if using `name`."
                )
            if self.given_names:
                raise ValueError(
                    "Do not specify `given_names` if using `name`."
                )
            return self

        raise ValueError(
            "Name must include either family_names and given_names fields, "
            "or a single name field."
        )


class Person(BaseModel):
    """Model for describing a person related to the technote."""

    name: PersonName

    internal_id: str | None = Field(
        None, description="An internal identifier for the person."
    )

    orcid: HttpUrl | None = Field(
        None, description="The ORCiD of the person (https://orcid.org)."
    )

    affiliations: list[Organization] = Field(
        default_factory=list, description="The person's affiliations."
    )

    email: EmailStr | None = Field(
        None, description="Contact email associated with the person."
    )

    @field_validator("orcid", mode="after")
    @classmethod
    def validate_orcid(cls, v: HttpUrl | None) -> HttpUrl | None:
        """Ensure that ``orcid`` is a valid ORCiD identifier, or `None`."""
        if v is not None:
            validate_orcid_url(v)
        return v

    @field_validator("orcid", mode="before")
    @classmethod
    def format_orcid_url(cls, value: str) -> str:
        """Format a bare ORCiD identifier as a URL."""
        if value.startswith(("http://oricid", "https://orcid")):
            return value
        if verify_orcid_checksum(value):
            return f"https://orcid.org/{value}"
        raise ValueError(f"Not an ORCiD identifier checksum ({value})")


class Contributor(Person):
    """Data about a contributor.

    A ``Contributor`` is the same as a ``Person``, with the addition of the
    `role` attribute.
    """

    role: ZenodoRole | None = Field(
        None, description="the contributor's role."
    )

    note: str | None = Field(
        None, description="Note describing the contribution."
    )


class LicenseTable(BaseModel):
    """A model for ``[technote.license]`` in ``technote.toml``, which
    describes the content's license.
    """

    id: str = Field(
        ...,
        description="The SPDX license ID. See https://spdx.org/licenses/.",
        examples=["CC-BY-SA-4.0"],
    )

    @field_validator("id")
    @classmethod
    def validate_spdx_id(cls, v: str) -> str:
        """Ensure that ``id`` is a SPDX license identifier."""
        if v is not None:
            licenses = Licenses.load()
            if v not in licenses:
                raise ValueError(
                    f"License ID '{v}' is not a valid SPDX license identifier."
                )
        return v


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


class Link(BaseModel):
    """A model for a web link."""

    url: HttpUrl = Field(description="The URL of the link.")

    title: str | None = Field(
        None,
        description="The title of the link, if available.",
    )


class TechnoteStatus(BaseModel):
    """A model for the technote's status.

    Status is intended to describe whether a document is in planning,
    active writing, stable, or deprecated/supersceded stages of its lifecycle.
    It's not intended for fine-grained status, such as describing a work ticket
    that's in progress or in review.
    """

    state: TechnoteState = Field(
        description="The state of a document, from a controlled vocabulary."
    )

    note: str | None = Field(None, description="An explanation of the state.")

    supersceding_urls: list[Link] = Field(
        default_factory=list,
        description=(
            "URLs to documents/webpages that superscede this technote."
        ),
    )


class TechnoteTable(BaseModel):
    """The root table for technote configuration, ``[technote]`` in
    ``technote.toml`` (`TechnoteToml`).
    """

    id: str | None = Field(
        None,
        description="An internal identifier for the technote.",
        examples=["SQR-000"],
    )

    series_id: str | None = Field(
        None,
        description=(
            "An internal identifier for a series this technote belongs to."
        ),
        examples=["SQR"],
    )

    date_created: datetime | None = Field(
        None, description="Date and time when the technote was created."
    )

    date_updated: datetime | None = Field(
        None, description="Date when the technote was updated."
    )

    version: str | None = Field(
        None, description="The current version of the technote."
    )

    doi: str | None = Field(
        None,
        description=(
            "The most-relevant DOI that identifies this technote. "
            "This can be a pre-registerered DOI (i.e. for Zenodo) so that the "
            "DOI can be present in the released technote source."
        ),
    )

    title: str | None = Field(
        None,
        description=(
            "The technote's title. Normally the title is derived from "
            "the document's source."
        ),
    )

    canonical_url: HttpUrl | None = Field(
        None,
        description="The URL where this technote is published.",
        examples=["https://sqr-000.lsst.io/"],
    )

    github_url: HttpUrl | None = Field(
        None,
        description="The URL of the GitHub repository hosting this technote.",
    )

    github_default_branch: str = Field(
        "main", description="The default branch of the GitHub repository."
    )

    status: TechnoteStatus | None = Field(
        None, description="The status of the technote."
    )

    license: LicenseTable | None = Field(
        None, description="The specification of a content license."
    )

    authors: list[Person] = Field(
        description="The authors of the technote.",
        default_factory=list,
    )

    contributors: list[Contributor] = Field(
        description="Additional persons involved.",
        default_factory=list,
    )

    sphinx: SphinxTable = Field(default_factory=SphinxTable)

    _normalize_dates = field_validator(
        "date_created", "date_updated", mode="before"
    )(normalize_datetime)


class TechnoteToml(BaseModel):
    """A model of a ``technote.toml`` configuration file."""

    technote: TechnoteTable

    @classmethod
    def parse_toml(cls, content: str) -> TechnoteToml:
        """Load a ``technote.toml`` file from the project directory.

        Parameters
        ----------
        content
            The string content of a ``technote.toml`` file.

        Returns
        -------
        TechnoteToml
            The parsed `TechnoteToml`.
        """
        return cls.model_validate(tomllib.loads(content))


@dataclass
class TechnoteSphinxConfig:
    """A wrapper around `TechnoteToml` that assists in setting Sphinx
    configurations in a conf.py file (via `technote.sphinxconf`).
    """

    toml: TechnoteToml
    """The parse ``technote.toml`` file."""

    @classmethod
    def find_and_load(cls) -> TechnoteSphinxConfig:
        """Find the ``technote.toml`` file in the current Sphinx build and
        load it.

        Returns
        -------
        TechnoteSphinxConfig
            The technote configuration, useful for configuring the Sphinx
            project.
        """
        path = Path("technote.toml")
        if not path.is_file():
            raise ConfigError("Cannot find the technote.toml file.")
        return cls.load(path.read_text())

    @classmethod
    def load(cls, toml_content: str) -> TechnoteSphinxConfig:
        """Load the content of a ``technote.toml`` file.

        Parameters
        ----------
        content
            The string content of a ``technote.toml`` file.

        Returns
        -------
        TechnoteSphinxConfig
            The sphinx configuration wrapper class around `TechnoteToml`.
        """
        try:
            parsed_toml = TechnoteToml.parse_toml(toml_content)
        except ValidationError as e:
            message = "Syntax or validation issue in technote.toml"
            raise ConfigError(message) from e

        return cls(toml=parsed_toml)

    @property
    def title(self) -> str | None:
        """The title of the document set via technote.toml metadata, or
        None if the document's H1 should be used.
        """
        return self.toml.technote.title

    @property
    def author(self) -> str:
        """A plaintext expression of the author or authors."""
        if self.toml.technote.authors:
            return ", ".join(
                a.name.plain_text_name for a in self.toml.technote.authors
            )
        else:
            return ""

    def append_extensions(self, extensions: list[str]) -> None:
        """Append user-configured extensions to an existing list."""
        for new_ext in self.toml.technote.sphinx.extensions:
            if new_ext not in extensions:
                extensions.append(new_ext)

    def extend_intersphinx_mapping(
        self, mapping: MutableMapping[str, tuple[str, str | None]]
    ) -> None:
        """Extend the ``intersphinx_mapping`` dictionary with configured
        projects.
        """
        for (
            project,
            url,
        ) in self.toml.technote.sphinx.intersphinx.projects.items():
            mapping[project] = (str(url), None)

    def append_linkcheck_ignore(self, link_patterns: list[str]) -> None:
        """Append URL patterns for sphinx.linkcheck.ignore to existing
        patterns.
        """
        link_patterns.extend(self.toml.technote.sphinx.linkcheck.ignore)

    def append_nitpick_ignore(
        self, nitpick_ignore: list[tuple[str, str]]
    ) -> None:
        """Append ``nitpick_ignore`` items from sphinx.nitpick_ignore."""
        nitpick_ignore.extend(self.toml.technote.sphinx.nitpick_ignore)

    def append_nitpick_ignore_regex(
        self, nitpick_ignore_regex: list[tuple[str, str]]
    ) -> None:
        """Append ``nitpick_ignore_regex`` items from sphinx.nitpick_ignore."""
        nitpick_ignore_regex.extend(
            self.toml.technote.sphinx.nitpick_ignore_regex
        )

    @property
    def nitpicky(self) -> bool:
        """The nitpicky boolean flag."""
        return self.toml.technote.sphinx.nitpicky

    @property
    def jinja_context(self) -> TechnoteJinjaContext:
        """The TechnoteJinjaContext that provides metadata to the HTML
        templates.
        """
        return TechnoteJinjaContext(toml=self.toml)


class TechnoteJinjaContext:
    """A class available to the Jinja context in HTML templates and
    provides access to technote.toml-based metadata.

    Parameters
    ----------
    toml
        The metadata from ``technote.toml``.
    """

    def __init__(self, toml: TechnoteToml) -> None:
        self._toml: TechnoteToml = toml
        self._content_title: str | None = None
        self._content_abstract: str | None = None

    @property
    def toml(self) -> TechnoteToml:
        """The technote.toml root object."""
        return self._toml

    @property
    def title(self) -> str:
        """The technote's title.

        The title is the ``h1`` heading from the document if
        ``technote.title`` isn't set in ``technote.toml``.
        """
        if self.toml.technote.title is not None:
            return self.toml.technote.title

        if self._content_title is None:
            raise RuntimeError(
                "The document is missing a heading for its title."
            )

        return self._content_title

    @property
    def abstract(self) -> str | None:
        """The technote's unformatted abstract.

        This content is extracted from the ``abstract`` directive, and all
        markup is removed as part of that process. This attribute can be used
        for populating summary tags in the HTML header.
        """
        return self._content_abstract

    @property
    def date_updated_iso(self) -> str | None:
        """The date updated, as an ISO 8601 string normalized to UTC."""
        if self.toml.technote.date_updated:
            return self._format_iso_date(self.toml.technote.date_updated)
        else:
            return None

    @property
    def date_created_iso(self) -> str | None:
        """The date of initial publication, as an ISO 8601 string
        normalized to UTC.
        """
        if self.toml.technote.date_created:
            return self._format_iso_date(self.toml.technote.date_created)
        else:
            return None

    @property
    def datetime_updated_iso(self) -> str | None:
        """The datetime updated, as an ISO 8601 string normalized to UTC."""
        if self.toml.technote.date_updated:
            return self._format_iso_datetime(self.toml.technote.date_updated)
        else:
            return None

    @property
    def datetime_created_iso(self) -> str | None:
        """The datetime of initial publication, as an ISO 8601 string
        normalized to UTC.
        """
        if self.toml.technote.date_created:
            return self._format_iso_datetime(self.toml.technote.date_created)
        else:
            return None

    @property
    def version(self) -> str | None:
        """The version, as a string if available."""
        return self.toml.technote.version

    @property
    def canonical_url(self) -> str | None:
        """The canonical URL of the technote, if available."""
        return str(self.toml.technote.canonical_url)

    @property
    def github_url(self) -> str | None:
        """The GitHub repository URL."""
        if self.toml.technote.github_url is None:
            return None
        else:
            return str(self.toml.technote.github_url)

    @property
    def github_repo_slug(self) -> str | None:
        """The GitHub repository slug, ``owner/name``."""
        if self.github_url is None:
            return self.github_url

        url_parts = urlparse(self.github_url)
        slug = "/".join(url_parts.path.lstrip("/").split("/")[:2])
        if slug.endswith(".git"):  # replace with str.removesuffix in 3.9+
            slug = slug[:-4]
        return slug

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
        if self.github_url.endswith(".git"):  # replace with str.removesuffix
            root_url = self.github_url[:-4]
        else:
            root_url = self.github_url

        # FIXME: compute source path during Sphinx build
        # We're using /blob/ instead of /edit/ to give users the choice of
        # how to edit (on web or in github.dev).
        return (
            f"{root_url}/blob/{self.toml.technote.github_default_branch}"
            "/index.rst"
        )

    def set_content_title(self, title: str) -> None:
        """Set the title from the content nodes."""
        self._content_title = title

    def set_abstract(self, abstract: str) -> None:
        """Set the abstract metadata from the content."""
        self._content_abstract = abstract

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
            metadata=self.toml.technote,
            title=self.title,
            abstract=self.abstract,
        )
        return highwire.as_html()

    @property
    def opengraph_metadata_tags(self) -> str:
        """The OpenGraph metadata tags for the technote."""
        og = OpenGraphMetadata(
            metadata=self.toml.technote,
            title=self.title,
            abstract=self.abstract,
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
