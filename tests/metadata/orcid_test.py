"""Tests for the technote.metadata.orcid module."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, HttpUrl, ValidationError, field_validator

from technote.metadata.orcid import validate_orcid_url, verify_checksum


class Model(BaseModel):
    """A model with an ORCiD type."""

    orcid: HttpUrl

    @field_validator("orcid", mode="after")
    @classmethod
    def validate_ror(cls, value: HttpUrl) -> HttpUrl:
        validate_orcid_url(value)
        return value

    @field_validator("orcid", mode="before")
    @classmethod
    def format_orcid_url(cls, value: str) -> str:
        if value.startswith(("http://oricid", "https://orcid")):
            return value
        if verify_checksum(value):
            return f"https://orcid.org/{value}"
        raise ValueError(f"Not an ORCiD identifier checksum ({value})")


@pytest.mark.parametrize(
    "sample",
    [
        "https://orcid.org/0000-0002-1825-0097",
        "https://orcid.org/0000-0001-5109-3700",
        "https://orcid.org/0000-0002-1694-233X",
        "0000-0002-1825-0097",
        "0000-0001-5109-3700",
        "0000-0002-1694-233X",
    ],
)
def test_orcid(sample: str) -> None:
    """Test that a model with an Orcid field can validate."""
    m = Model(orcid=sample)

    assert m.orcid.host == "orcid.org"
    assert m.orcid.scheme == "https"

    assert m.orcid.path
    identifier = m.orcid.path[1:]
    assert verify_checksum(identifier)


@pytest.mark.parametrize("sample", ["0000-0002-1825-0099", "0001-5109-3700"])
def test_orcid_fail(sample: str) -> None:
    """Test mal-formed ORCiD (wrong checksum or wrong pattern)."""
    with pytest.raises(ValidationError):
        Model(orcid=sample)
