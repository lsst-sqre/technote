"""Tests for the technote.sources.tomlsettings module."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from technote.sources.tomlsettings import TechnoteToml

sample_toml = """
[technote]
id = "SQR-000"
title = "The LSST DM Technical Note Publishing Platform"
date_created = "2015-11-18"
date_updated = "2015-11-23T15:00:00Z"
canonical_url = "https://sqr-000.lsst.io/"
github_url = "https://github.com/lsst-sqre/sqr-000"
version = "1.0.0"
license = { id = "CC-BY-4.0" }

[[technote.authors]]
name.given = "Jonathan"
name.family = "Sick"
orcid = "https://orcid.org/0000-0003-3001-676X"
affiliations = [
    { name = "Rubin Observatory", ror = "https://ror.org/048g3cy84" }
]
"""


def test_toml_parsing() -> None:
    """Test TechnoteToml by parsing a sample document that should be
    well-formatted.
    """
    technote_toml = TechnoteToml.parse_toml(sample_toml)
    assert technote_toml.technote.id == "SQR-000"


def test_toml_doi() -> None:
    """Test that a DOI in technote.toml is normalized to its bare form."""
    toml_content = (
        '[technote]\ndoi = "https://doi.org/10.5281/zenodo.10385500"\n'
    )
    technote_toml = TechnoteToml.parse_toml(toml_content)
    assert technote_toml.technote.doi == "10.5281/zenodo.10385500"


def test_toml_doi_with_prefix_space() -> None:
    """Test a ``doi:`` prefix separated from the DOI by a space."""
    toml_content = '[technote]\ndoi = "doi: 10.5281/zenodo.10385500"\n'
    technote_toml = TechnoteToml.parse_toml(toml_content)
    assert technote_toml.technote.doi == "10.5281/zenodo.10385500"


def test_toml_doi_default() -> None:
    """Test that the DOI is None when it is not set."""
    technote_toml = TechnoteToml.parse_toml(sample_toml)
    assert technote_toml.technote.doi is None


@pytest.mark.parametrize("value", ["", "   "])
def test_toml_doi_empty_string(value: str) -> None:
    """Test that an empty ``doi`` string is treated as an unset DOI."""
    technote_toml = TechnoteToml.parse_toml(f'[technote]\ndoi = "{value}"\n')
    assert technote_toml.technote.doi is None


def test_toml_invalid_doi() -> None:
    """Test that an invalid DOI in technote.toml is a validation error."""
    with pytest.raises(ValidationError, match="Not a DOI"):
        TechnoteToml.parse_toml('[technote]\ndoi = "not-a-doi"\n')


def test_toml_non_string_doi() -> None:
    """Test that an unquoted (non-string) DOI is a validation error."""
    with pytest.raises(ValidationError, match="doi") as exc_info:
        TechnoteToml.parse_toml("[technote]\ndoi = 10.5281\n")
    assert "Not a DOI" in str(exc_info.value)


def test_toml_lint_default() -> None:
    """The lint table defaults to ignoring no rules."""
    technote_toml = TechnoteToml.parse_toml(sample_toml)
    assert technote_toml.technote.lint.ignore == []


def test_toml_lint_ignore() -> None:
    """Test that rule codes in ``[technote.lint] ignore`` are parsed."""
    toml_content = (
        sample_toml + '\n[technote.lint]\nignore = ["TN105", "R101"]\n'
    )
    technote_toml = TechnoteToml.parse_toml(toml_content)
    assert technote_toml.technote.lint.ignore == ["TN105", "R101"]


@pytest.mark.parametrize(
    "code", ["tn105", "105", "TN", "TN-105", " TN105", "TN105a"]
)
def test_toml_lint_ignore_invalid_code(code: str) -> None:
    """A code that isn't an uppercase prefix plus a number is a config
    error.
    """
    toml_content = sample_toml + f'\n[technote.lint]\nignore = ["{code}"]\n'
    with pytest.raises(ValidationError, match="Not a lint rule code"):
        TechnoteToml.parse_toml(toml_content)
