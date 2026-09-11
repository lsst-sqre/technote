"""Tests for the technote.factory module."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

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
