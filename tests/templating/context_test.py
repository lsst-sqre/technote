"""Tests for the technote.templating.TechnoteJinjaContext module."""

from __future__ import annotations

from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from technote.factory import Factory

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


def test_technote_jinja_context(monkeypatch: MonkeyPatch) -> None:
    """Test TechnoteJinjaContext with the sample toml."""
    monkeypatch.setenv("GITHUB_REF_NAME", "main")
    monkeypatch.setenv("GITHUB_REF_TYPE", "branch")

    factory = Factory()
    technote_toml = factory.parse_toml(sample_toml)
    factory._toml = technote_toml
    metadata = factory.load_metadata()
    jinja_context = factory.create_jinja_context(
        metadata=metadata, root_filename=Path("index.rst")
    )

    assert jinja_context.github_url == "https://github.com/lsst-sqre/sqr-000"
    assert jinja_context.github_repo_slug == "lsst-sqre/sqr-000"
    assert jinja_context.github_ref_name == "main"
    assert jinja_context.github_ref_type == "branch"
