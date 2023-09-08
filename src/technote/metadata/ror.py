"""Support for ROR (Research Organization Registry) identifiers."""

from __future__ import annotations

import re

import base32_lib as base32
from pydantic import HttpUrl

__all__ = ["validate_ror_url"]

ROR_PATTERN = re.compile(
    r"https://ror.org"
    r"\/(?P<identifier>0[0-9abcdefghjkmpqrstuvwxyzabcdefghjkmpqrstuvwxyz]{8})",
    flags=re.IGNORECASE,
)


def validate_ror_url(value: HttpUrl) -> None:
    """Check a ROR URL for validity.

    Raises
    ------
    ValueError
        Raised if the URL is not a valid ROR URL.
    """
    m = ROR_PATTERN.search(str(value))
    if not m:
        raise ValueError(f"Expected ROR URL, received: {value}")
    identifier = m["identifier"]
    try:
        base32.decode(identifier, checksum=True)
    except ValueError as e:
        raise ValueError("ROR identifier checksum failed") from e
