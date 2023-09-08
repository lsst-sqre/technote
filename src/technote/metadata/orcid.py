"""The ORCiD identifier."""

from __future__ import annotations

import re

from pydantic import HttpUrl

__all__ = ["validate_orcid_url"]


ORCID_PATTERN = re.compile(
    r"(?P<identifier>[0-9X]{4}-[0-9X]{4}-[0-9X]{4}-[0-9X]{4})"
)
"""Regular expression for matching the ORCiD identifier.

Examples:

- 0000-0002-1825-0097
- 0000-0001-5109-3700
- 0000-0002-1694-233X

For more information, see
https://support.orcid.org/hc/en-us/articles/360006897674
"""


def validate_orcid_url(value: HttpUrl) -> None:
    """Check an ORCiD URL for validity.

    Raises
    ------
    ValueError
        Raised if the URL is not a valid ROR URL.
    """
    m = ORCID_PATTERN.search(str(value))
    if not m:
        raise ValueError(f"Expected ORCiD URL, received: {value}")

    identifier = m["identifier"]
    if not verify_checksum(identifier):
        raise ValueError(f"ORCiD identifier checksum failed ({value})")


def verify_checksum(identifier: str) -> bool:
    """Verify the checksum of an ORCiD identifier string (path component
    of the URL) given the ISO 7064 11,2 algorithm.
    """
    total: int = 0
    for digit in identifier:
        numeric_digit = "10" if digit == "X" else digit
        if not numeric_digit.isdigit():
            continue
        total = (total + int(numeric_digit)) * 2
    remainder = total % 11
    result = (12 - remainder) % 11
    return result == 10
