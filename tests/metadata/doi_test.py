"""Tests for the technote.metadata.doi module."""

from __future__ import annotations

import pytest

from technote.metadata.doi import normalize_doi


@pytest.mark.parametrize(
    "value",
    [
        "10.5281/zenodo.10385500",
        "https://doi.org/10.5281/zenodo.10385500",
        "http://doi.org/10.5281/zenodo.10385500",
        "https://dx.doi.org/10.5281/zenodo.10385500",
        "http://dx.doi.org/10.5281/zenodo.10385500",
        "doi:10.5281/zenodo.10385500",
        "doi: 10.5281/zenodo.10385500",
        "https://doi.org/ 10.5281/zenodo.10385500",
        "  10.5281/zenodo.10385500  ",
    ],
)
def test_normalize_doi(value: str) -> None:
    """Test that DOIs are normalized to their bare form."""
    assert normalize_doi(value) == "10.5281/zenodo.10385500"


@pytest.mark.parametrize(
    "value",
    [
        "zenodo.10385500",
        "https://example.com/10.5281/zenodo.10385500",
        "11.5281/zenodo.10385500",
        "10.5281",
        "",
    ],
)
def test_normalize_doi_invalid(value: str) -> None:
    """Test that values that are not DOIs are rejected."""
    with pytest.raises(ValueError, match="Not a DOI"):
        normalize_doi(value)
