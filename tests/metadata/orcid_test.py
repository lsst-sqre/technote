"""Tests for the technote.metadata.orcid module."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from technote.metadata.orcid import Orcid


@pytest.mark.parametrize(
    "identifier,sample",
    [
        ("0000-0002-1825-0097", "0000-0002-1825-0097"),
        ("0000-0001-5109-3700", "hello 0000-0001-5109-3700 world"),
        ("0000-0002-1694-233X", "0000-0002-1694-233X"),
        ("0000-0002-1825-0097", "https://orcid.org/0000-0002-1825-0097"),
        ("0000-0001-5109-3700", "http://0000-0001-5109-3700"),
        ("0000-0002-1694-233X", "https://0000-0002-1694-233X"),
    ],
)
def test_orcid(identifier: str, sample: str) -> None:
    """Test that a model with an Orcid field can validate."""

    class Model(BaseModel):
        orcid: Orcid

    m = Model(orcid=sample)

    assert m.orcid == f"https://orcid.org/{identifier}"
    assert m.orcid.path == f"/{identifier}"
    assert m.orcid.host == "orcid.org"
    assert m.orcid.scheme == "https"


@pytest.mark.parametrize("sample", ["0000-0002-1825-0099", "0001-5109-3700"])
def test_orcid_fail(sample: str) -> None:
    """Test mal-formed ORCiD (wrong checksum or wrong pattern)."""

    class Model(BaseModel):
        orcid: Orcid

    with pytest.raises(ValidationError):
        Model(orcid=sample)
