"""Tests for the technote.factory module."""

from __future__ import annotations

import tomllib
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from sphinx.errors import ConfigError

from technote.factory import Factory

sample_toml = """
[technote]
id = "SQR-000"
title = "The LSST DM Technical Note Publishing Platform"
date_created = 2026-09-12
"""
"""A technote created on 2026-09-12, with no declared ``date_updated``.

The bare date is anchored to midnight UTC.
"""


def test_load_metadata_clamps_date_updated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A derived date_updated that precedes date_created is clamped.

    ``SOURCE_DATE_EPOCH`` here is 2026-09-11T21:00Z, which is the morning of
    2026-09-12 for an author in UTC+12 but the previous day in UTC.
    """
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1789160400")

    factory = Factory()
    factory.parse_toml(sample_toml)
    metadata = factory.load_metadata()

    assert metadata.date_created == datetime(2026, 9, 12, tzinfo=UTC)
    assert metadata.date_updated == metadata.date_created


def test_parse_toml_reports_a_validation_error() -> None:
    """A technote.toml that does not validate stops the build with a report
    in the file's own vocabulary, not with a sentence about the model.
    """
    with pytest.raises(ConfigError) as exc_info:
        Factory().parse_toml('[technote]\ndoi = "10.71929"\n')

    message = str(exc_info.value)
    assert message.startswith("Configuration error in technote.toml:")
    assert "[technote] doi" in message
    assert "Not a DOI (10.71929)." in message
    assert "Syntax or validation issue" not in message


def test_parse_toml_chains_the_validation_error() -> None:
    """The pydantic exception stays chained to the configuration error, so
    the traceback Sphinx saves still has everything needed to debug the model
    itself.
    """
    with pytest.raises(ConfigError) as exc_info:
        Factory().parse_toml('[technote]\ndoi = "10.71929"\n')

    assert isinstance(exc_info.value.__cause__, ValidationError)


def test_parse_toml_reports_a_syntax_error() -> None:
    """A file TOML itself cannot parse is reported as a configuration error
    naming the file and the place the parser stopped, rather than escaping as
    the parser's own exception.
    """
    with pytest.raises(ConfigError) as exc_info:
        Factory().parse_toml("[technote\ntitle='x'\n")

    message = str(exc_info.value)
    assert "Syntax error in technote.toml" in message
    assert "line 1" in message
    assert isinstance(exc_info.value.__cause__, tomllib.TOMLDecodeError)
