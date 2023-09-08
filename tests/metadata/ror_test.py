"""Tests for the technote.metadata.ror module."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, HttpUrl, field_validator

from technote.metadata.ror import validate_ror_url


class Model(BaseModel):
    """A model with a ROR type."""

    ror: HttpUrl

    @field_validator("ror", mode="after")
    @classmethod
    def validate_ror(cls, value: HttpUrl) -> HttpUrl:
        validate_ror_url(value)
        return value


def test_validate_ror() -> None:
    """Test that a model with a ROR type can be valid."""
    Model(ror="https://ror.org/02y72wh86")


@pytest.mark.parametrize(
    "sample",
    [
        "02y72wh86",  # not a URL
        "https://ror.org/02y72wh87",  # checksum should fail
        "https://roar.org/02y72wh86",  # wrong domain
    ],
)
def test_ror_fail(sample: str) -> None:
    """Test that a pydantic model with incorrect ROR values fail."""
    with pytest.raises(ValueError):  # noqa: PT011
        Model(ror=sample)
