"""Tests for the technote.config module."""

from __future__ import annotations

from _pytest.monkeypatch import MonkeyPatch

from technote.config import TechnoteJinjaContext, TechnoteToml

sample_toml = """
[technote]
id = "SQR-000"
title = "The LSST DM Technical Note Publishing Platform"
date_updated = "2015-11-23"
canonical_url = "https://sqr-000.lsst.io/"
github_url = "https://github.com/lsst-sqre/sqr-000"
version = "1.0.0"
license = { id = "CC-BY-4.0" }

[[technote.authors]]
name = { family_names = "Sick", given_names = "Jonathan" }
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


def test_technote_jinja_context(monkeypatch: MonkeyPatch) -> None:
    """Test TechnoteJinjaContext with the sample toml."""
    monkeypatch.setenv("GITHUB_REF_NAME", "main")
    monkeypatch.setenv("GITHUB_REF_TYPE", "branch")

    technote_toml = TechnoteToml.parse_toml(sample_toml)
    jinja_context = TechnoteJinjaContext(toml=technote_toml)

    assert jinja_context.github_url == "https://github.com/lsst-sqre/sqr-000"
    assert jinja_context.github_repo_slug == "lsst-sqre/sqr-000"
    assert jinja_context.github_ref_name == "main"
    assert jinja_context.github_ref_type == "branch"
