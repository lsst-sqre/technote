"""Models for the ``technote.toml`` configuration file."""

# Design note
#
# Keep in mind that technote.toml is a configuration file, not a metadata
# export schema. Some metadata can be discovered from the content, and
# reformatted from data in technote.toml (for example, a ORCiD can stand
# in for an author's name, and a ROR can stand in for the name of an
# affiliation.)

from __future__ import annotations

import re
import tomllib
from datetime import UTC, date, datetime
from typing import Any, Self

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from ..metadata.model import TechnoteState
from ..metadata.orcid import validate_orcid_url
from ..metadata.orcid import verify_checksum as verify_orcid_checksum
from ..metadata.ror import validate_ror_url
from ..metadata.spdx import Licenses
from ..metadata.zenodo import ZenodoRole

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
    if isinstance(v, date):
        return datetime.combine(v, datetime.min.time(), tzinfo=UTC)
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

    family: str = Field(
        description="The person's family name (last name in western culture).",
    )

    given: str = Field(
        description="The person's given name (first name in western culture).",
    )

    @field_validator("family", "given")
    @classmethod
    def clean_whitespace(cls, v: str | None) -> str | None:
        if v:
            return collapse_whitespace(v)
        else:
            return v


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

    organization: Organization | None = Field(
        None,
        description="The organization that publishes the technote series.",
    )

    date_created: datetime | date | None = Field(
        None, description="Date and time when the technote was created."
    )

    date_updated: datetime | date | None = Field(
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

    @property
    def date_created_datetime(self) -> datetime | None:
        """The ``date_created`` as a `~datetime.datetime`."""
        return normalize_datetime(self.date_created)

    @property
    def date_updated_datetime(self) -> datetime | None:
        """The ``date_updatd`` as a `~datetime.datetime`."""
        return normalize_datetime(self.date_updated)


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
