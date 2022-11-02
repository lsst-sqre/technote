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
# affiliation.

from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Extra,
    Field,
    HttpUrl,
    root_validator,
    validator,
)

from .metadata.orcid import Orcid
from .metadata.ror import Ror
from .metadata.spdx import Licenses
from .metadata.zenodo import ZenodoRole

__all__ = [
    "TechnoteToml",
    "Organization",
    "PersonName",
    "Person",
    "Contributor",
    "LicenseConfig",
    "TechnoteConfig",
]


WHITESPACE_PATTERN = re.compile(r"\s+")


def collapse_whitespace(text: str) -> str:
    """Replace any whitespace character, or group, with a single space."""
    return WHITESPACE_PATTERN.sub(" ", text).strip()


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

    surname: Optional[str] = Field(
        None,
        description="The person's family name (last name in western culture).",
    )

    given: Optional[str] = Field(
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

    @validator("surname", "given", "name")
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
        if values.get("surname") and values.get("given"):
            if values.get("name"):
                raise ValueError(
                    "Do not specify name if surname and given names are "
                    "both provided."
                )
            return values
        if values.get("name"):
            if values.get("surname"):
                raise ValueError("Do not specify `surname` if using `name`.")
            elif values.get("given"):
                raise ValueError("Do not specify `given` if using `name`.")
            return values

        raise ValueError(
            "Name must include either surname and given fields, or a single "
            "name field."
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


class LicenseConfig(BaseModel):
    """A model for configuring a content license."""

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


class TechnoteConfig(BaseModel):
    """The root table for technote configuration, ``[technote]`` in
    technote.toml.
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

    license: Optional[LicenseConfig] = Field(
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


class TechnoteToml(BaseModel, extra=Extra.ignore):
    """A model of a ``technote.toml`` configuration file."""

    technote: TechnoteConfig
