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
import sys
from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, Optional, Tuple, Union
from urllib.parse import urlparse

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

from pydantic import (
    BaseModel,
    EmailStr,
    Extra,
    Field,
    HttpUrl,
    ValidationError,
    root_validator,
    validator,
)
from sphinx.errors import ConfigError

from .metadata.orcid import Orcid
from .metadata.ror import Ror
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


class IntersphinxTable(BaseModel):
    """Intersphinx configuration in the ``[technote.sphinx]`` table."""

    projects: Dict[str, HttpUrl] = Field(
        description="Mapping of projects and their URLs.", default_factory=dict
    )


class LinkcheckTable(BaseModel):
    """Linkcheck builder configurations in the ``[technote.sphinx]`` table."""

    ignore: List[str] = Field(
        description="Regular expressions of URLs to skip checking links",
        default_factory=list,
    )


class SphinxTable(BaseModel):
    """The ``[technote.sphinx]`` table permits Sphinx project configuration."""

    nitpicky: bool = Field(
        False, description="Escalate warnings to build errors."
    )

    nitpick_ignore: List[Tuple[str, str]] = Field(
        description=(
            "Errors to ignore. First item is the type (like a role or "
            "directive) and the second is the target (like the argument to "
            "the role)."
        ),
        default_factory=list,
    )

    nitpick_ignore_regex: List[Tuple[str, str]] = Field(
        description=(
            "Same as ``nitpick_ignore``, but both type and target are "
            "interpreted as regular expressions."
        ),
        default_factory=list,
    )

    extensions: List[str] = Field(
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

    internal_id: Optional[str] = Field(
        None, description="A user-specific identifier for an organization."
    )

    ror: Optional[Ror] = Field(
        None, description="The ROR (ror.org) identifier of the institution."
    )

    name: Optional[str] = Field(
        None, description="The display name of the institution."
    )

    address: Optional[str] = Field(
        None, description="The address of the institution."
    )

    url: Optional[HttpUrl] = Field(
        None, description="The homepage of the institution."
    )

    @validator("name")
    def clean_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return collapse_whitespace(v)
        else:
            return v

    @root_validator
    def check_well_defined(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure that at least the internal ID, ROR, or name are provided."""
        if values.get("internal_id"):
            return values
        if values.get("ror"):
            return values
        if values.get("name"):
            return values

        raise ValueError(
            "An organization must have a name, ror, or internal_id"
        )


class PersonName(BaseModel):
    """A person's name."""

    family_names: Optional[str] = Field(
        None,
        description="The person's family name (last name in western culture).",
    )

    given_names: Optional[str] = Field(
        None,
        description="The person's given name (first name in western culture).",
    )

    name: Optional[str] = Field(
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

    @validator("family_names", "given_names", "name")
    def clean_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return collapse_whitespace(v)
        else:
            return v

    @root_validator
    def check_well_defined(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Check that either surname and given are both provided, or name
        alone is set
        """
        if values.get("family_names") and values.get("given_names"):
            if values.get("name"):
                raise ValueError(
                    "Do not specify name if family_names and given_names are "
                    "both provided."
                )
            return values
        if values.get("name"):
            if values.get("family_names"):
                raise ValueError(
                    "Do not specify `family_names` if using `name`."
                )
            elif values.get("given_names"):
                raise ValueError(
                    "Do not specify `given_names` if using `name`."
                )
            return values

        raise ValueError(
            "Name must include either family_names and given_names fields, "
            "or a single name field."
        )


class Person(BaseModel):
    """Model for describing a person related to the technote."""

    name: PersonName

    internal_id: Optional[str] = Field(
        None, description="An internal identifier for the person."
    )

    orcid: Optional[Orcid] = Field(
        None, description="The ORCiD of the person (https://orcid.org)."
    )

    affiliations: Optional[List[Organization]] = Field(
        default_factory=list, description="The person's affiliations."
    )

    email: Optional[EmailStr] = Field(
        description="Contact email associated with the person."
    )


class Contributor(Person):
    """Data about a contributor.

    A ``Contributor`` is the same as a ``Person``, with the addition of the
    `role` attribute.
    """

    role: Optional[ZenodoRole] = Field(
        None, description="the contributor's role."
    )

    note: Optional[str] = Field(
        None, description="Note describing the contribution."
    )


class LicenseTable(BaseModel):
    """A model for ``[technote.license]`` in ``technote.toml``, which
    describes the content's license.
    """

    id: str = Field(
        ...,
        description="The SPDX license ID. See https://spdx.org/licenses/.",
        examples="CC-BY-SA-4.0",
    )

    @validator("id")
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
         planning --> active
         active --> stable
         stable --> active
         stable --> deprecated
         active --> deprecated
    """

    planning = "planning"
    """The technote is being researched and planned, but may not have useful
    content yet.
    """

    active = "active"
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

    note: Optional[str] = Field(
        None, description="An explanation of the state."
    )

    supersceding_urls: List[HttpUrl] = Field(
        default_factory=list,
        description=(
            "URLs to documents/webpages that superscede this technote."
        ),
    )


class TechnoteTable(BaseModel):
    """The root table for technote configuration, ``[technote]`` in
    ``technote.toml`` (`TechnoteToml`).
    """

    id: Optional[str] = Field(
        None,
        description="An internal identifier for the technote.",
        examples="SQR-000",
    )

    series_id: Optional[str] = Field(
        None,
        description=(
            "An internal identifier for a series this technote belongs to."
        ),
        examples="SQR",
    )

    date_created: Optional[date] = Field(
        None, description="Date when the technote was created."
    )

    date_updated: Optional[date] = Field(
        None, description="Date when the technote was updated."
    )

    version: Optional[str] = Field(
        None, description="The current version of the technote."
    )

    doi: Optional[str] = Field(
        None,
        description=(
            "The most-relevant DOI that identifies this technote. "
            "This can be a pre-registerered DOI (i.e. for Zenodo) so that the "
            "DOI can be present in the released technote source."
        ),
    )

    title: Optional[str] = Field(
        None,
        description=(
            "The technote's title. Normally the title is derived from "
            "the document's source."
        ),
    )

    canonical_url: Optional[HttpUrl] = Field(
        None,
        description="The URL where this technote is published.",
        examples="https://sqr-000.lsst.io",
    )

    github_url: Optional[HttpUrl] = Field(
        None,
        description="The URL of the GitHub repository hosting this technote.",
    )

    github_default_branch: str = Field(
        "main", description="The default branch of the GitHub repository."
    )

    status: Optional[TechnoteStatus] = Field(
        None, description="The status of the technote."
    )

    license: Optional[LicenseTable] = Field(
        None, description="The specification of a content license."
    )

    authors: List[Person] = Field(
        description="The authors of the technote.",
        default_factory=list,
    )

    contributors: List[Contributor] = Field(
        description="Additional persons involved.",
        default_factory=list,
    )

    sphinx: SphinxTable = Field(default_factory=SphinxTable)


class TechnoteToml(BaseModel, extra=Extra.ignore):
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
        return cls.parse_obj(tomllib.loads(content))


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
            message = (
                f"Syntax or validation issue in technote.toml:\n\n" f"{str(e)}"
            )
            raise ConfigError(message)

        return cls(toml=parsed_toml)

    @property
    def title(self) -> Optional[str]:
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

    def append_extensions(self, extensions: List[str]) -> None:
        """Append user-configured extensions to an existing list."""
        for new_ext in self.toml.technote.sphinx.extensions:
            if new_ext not in extensions:
                extensions.append(new_ext)

    def extend_intersphinx_mapping(
        self, mapping: MutableMapping[str, Tuple[str, Union[str, None]]]
    ) -> None:
        """Extend the ``intersphinx_mapping`` dictionary with configured
        projects.
        """
        for (
            project,
            url,
        ) in self.toml.technote.sphinx.intersphinx.projects.items():
            mapping[project] = (str(url), None)

    def append_linkcheck_ignore(self, link_patterns: List[str]) -> None:
        """Append URL patterns for sphinx.linkcheck.ignore to existing
        patterns.
        """
        link_patterns.extend(self.toml.technote.sphinx.linkcheck.ignore)

    def append_nitpick_ignore(
        self, nitpick_ignore: List[Tuple[str, str]]
    ) -> None:
        """Append ``nitpick_ignore`` items from sphinx.nitpick_ignore."""
        nitpick_ignore.extend(self.toml.technote.sphinx.nitpick_ignore)

    def append_nitpick_ignore_regex(
        self, nitpick_ignore_regex: List[Tuple[str, str]]
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
        self._content_title: Optional[str] = None
        self._content_abstract: Optional[str] = None

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
        else:
            if self._content_title is None:
                raise RuntimeError(
                    "The document is missing a heading for its title."
                )
            else:
                return self._content_title

    @property
    def abstract(self) -> str:
        """The technote's unformatted abstract.

        This content is extracted from the ``abstract`` directive, and all
        markup is removed as part of that process. This attribute can be used
        for populating summary tags in the HTML header.
        """
        if self._content_abstract:
            return self._content_abstract
        else:
            return "N/A"

    @property
    def date_updated_iso(self) -> Optional[str]:
        """The date updated, as an ISO 8601 string."""
        if self.toml.technote.date_updated:
            return self._format_iso_date(self.toml.technote.date_updated)
        else:
            return None

    @property
    def version(self) -> Optional[str]:
        """The version, as a string if available."""
        return self.toml.technote.version

    @property
    def github_url(self) -> Optional[str]:
        """The GitHub repository URL."""
        return self.toml.technote.github_url

    @property
    def github_repo_slug(self) -> Optional[str]:
        """The GitHub repository slug, ``owner/name``."""
        if self.github_url is None:
            return self.github_url

        url_parts = urlparse(self.github_url)
        slug = "/".join(url_parts.path.lstrip("/").split("/")[:2])
        if slug.endswith(".git"):  # replace with str.removesuffix in 3.9+
            slug = slug[:-4]
        return slug

    @property
    def github_ref_name(self) -> Optional[str]:
        """The branch or tag name."""
        # FIXME this is calculated from GitHub Actions environment variables
        # https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables
        return os.getenv("GITHUB_REF_NAME")

    @property
    def github_ref_type(self) -> Optional[str]:
        """The ref type: branch or tag."""
        # FIXME this is calculated from GitHub Actions environment variables
        # https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables
        return os.getenv("GITHUB_REF_TYPE")

    @property
    def github_edit_url(self) -> Optional[str]:
        """The URL for editing content on GitHub, from its default branch."""
        if self.github_url is None:
            return None
        if self.github_url.endswith(".git"):  # replace with str.removesuffix
            root_url = self.github_url[:-4]
        else:
            root_url = self.github_url

        # FIXME compute source path during Sphinx build
        # We're using /blob/ instead of /edit/ to give users the choice of
        # how to edit (on web or in github.dev).
        edit_url = (
            f"{root_url}/blob/{self.toml.technote.github_default_branch}"
            "/index.rst"
        )
        return edit_url

    def set_content_title(self, title: str) -> None:
        """Set the title from the content nodes."""
        self._content_title = title

    def set_abstract(self, abstract: str) -> None:
        """Set the abstract metadata from the content."""
        self._content_abstract = abstract

    def _format_iso_date(self, date: date) -> str:
        """Format a date in ISO 8601 format."""
        return date.isoformat()
