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


@pytest.mark.parametrize(
    "ror_url",
    [
        "https://ror.org/048g3cy84",  # Rubin Observatory
        "https://ror.org/05gzmn429",  # SLAC
        "https://ror.org/00b93bs30",  # American Astronomical Society
        "https://ror.org/02jbv0t02",  # Lawrence Berkeley National Laboratory
        "https://ror.org/01ggx4157",  # CERN
        "https://ror.org/02y72wh86",  # Queen's University
    ],
)
def test_validate_ror_known_valid(ror_url: str) -> None:
    """Test that known valid ROR identifiers pass validation."""
    Model.model_validate({"ror": ror_url})


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
        Model.model_validate({"ror": sample})
