"""The ORCiD identifier."""

from __future__ import annotations

import re
from typing import Any, Generator

from pydantic import BaseConfig, HttpUrl
from pydantic.errors import UrlError
from pydantic.fields import ModelField
from pydantic.typing import AnyCallable

__all__ = ["Orcid", "OrcidError"]


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


class OrcidError(UrlError):
    """An error validating an ORCiD identifier, raised by Pydantic."""

    code = "orcid"
    msg_template = "invalid ORCiD"


class Orcid(HttpUrl):
    """An ORCiD type for Pydantic validation.

    The validator forces an ORCiD identifier to always be a URL for
    orcid.org, per https://support.orcid.org/hc/en-us/articles/360006897674.
    This validator implments the ISO 7064 11,2 checksum algorithm.
    """

    allowed_schemes = {"https"}

    @classmethod
    def __get_validators__(cls) -> Generator[AnyCallable, None, None]:
        yield cls.validate

    @classmethod
    def validate(
        cls, value: Any, field: ModelField, config: BaseConfig
    ) -> Orcid:
        if value.__class__ == cls:
            return value

        m = ORCID_PATTERN.search(value)
        if not m:
            raise OrcidError()

        identifier = m["identifier"]
        if not cls.verify_checksum(identifier):
            raise OrcidError()

        return HttpUrl.validate(
            f"https://orcid.org/{identifier}", field, config
        )

    @staticmethod
    def verify_checksum(identifier: str) -> bool:
        """Verify the checksum of an ORCiD identifier string (path component
        of the URL) given the ISO 7064 11,2 algorithm.
        """
        total: int = 0
        for digit in identifier:
            if digit == "X":
                digit = "10"
            if not digit.isdigit():
                continue
            total = (total + int(digit)) * 2
        remainder = total % 11
        result = (12 - remainder) % 11
        return result == 10
