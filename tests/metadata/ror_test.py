"""Tests for the technote.metadata.ror module."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from technote.metadata.ror import Ror


def test_ror() -> None:
    """Test that a model with a ROR type can be valid."""

    class Model(BaseModel):
        ror: Ror

    sample = "https://ror.org/02y72wh86"
    m = Model(ror=sample)
    assert m.ror == sample


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

    class Model(BaseModel):
        ror: Ror

    with pytest.raises(ValidationError):
        Model(ror=sample)
