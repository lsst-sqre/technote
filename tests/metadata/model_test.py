"""Tests for the technote.metadata.model module."""

from __future__ import annotations

import pytest

from technote.metadata.model import Citation


@pytest.mark.parametrize(
    "value",
    [
        "10.5281/zenodo.10385500",
        "https://doi.org/10.5281/zenodo.10385500",
        "doi:10.5281/zenodo.10385500",
        "  10.5281/zenodo.10385500  ",
    ],
)
def test_citation_doi_normalization(value: str) -> None:
    """Test that a Citation normalizes its DOI to the bare form, whatever
    form the DOI is constructed with.
    """
    citation = Citation(doi=value)
    assert citation.doi == "10.5281/zenodo.10385500"
    assert citation.doi_url == "https://doi.org/10.5281/zenodo.10385500"


def test_citation_invalid_doi() -> None:
    """Test that a Citation rejects a value that is not a DOI."""
    with pytest.raises(ValueError, match="Not a DOI"):
        Citation(doi="not-a-doi")


def test_citation_without_doi() -> None:
    """Test that a Citation without a DOI has no DOI URL."""
    citation = Citation()
    assert citation.doi is None
    assert citation.doi_url is None
