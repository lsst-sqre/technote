"""Shared date and time formatting for HTML metadata."""

from __future__ import annotations

from datetime import UTC, datetime

__all__ = ["format_iso_date", "format_iso_datetime", "format_slash_date"]


def format_iso_date(dt: datetime) -> str:
    """Format a datetime as an ISO 8601 date (``YYYY-MM-DD``) in UTC.

    Parameters
    ----------
    dt
        The datetime to format. A naive datetime is interpreted as UTC;
        an aware datetime is converted to UTC.

    Returns
    -------
    str
        The UTC date.
    """
    return _normalize_to_utc(dt).strftime("%Y-%m-%d")


def format_slash_date(dt: datetime) -> str:
    """Format a datetime as a slash-separated date (``YYYY/MM/DD``) in UTC.

    This is the date format that Highwire metadata tags use.

    Parameters
    ----------
    dt
        The datetime to format. A naive datetime is interpreted as UTC;
        an aware datetime is converted to UTC.

    Returns
    -------
    str
        The UTC date.
    """
    return _normalize_to_utc(dt).strftime("%Y/%m/%d")


def format_iso_datetime(dt: datetime) -> str:
    """Format a datetime as an ISO 8601 datetime
    (``YYYY-MM-DDTHH:MM:SSZ``) in UTC.

    Parameters
    ----------
    dt
        The datetime to format. A naive datetime is interpreted as UTC;
        an aware datetime is converted to UTC.

    Returns
    -------
    str
        The UTC datetime.
    """
    return _normalize_to_utc(dt).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_to_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC, treating a naive datetime as UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)
