"""Support for ROR (Research Organization Registry) identifiers."""

from __future__ import annotations

import re
from typing import Any, Generator

import base32_lib as base32
from pydantic import BaseConfig, HttpUrl
from pydantic.errors import UrlError
from pydantic.fields import ModelField
from pydantic.typing import AnyCallable

__all__ = ["Ror", "RorError"]

ROR_PATTERN = re.compile(
    r"https://ror.org"
    r"\/(?P<identifier>0[0-9abcdefghjkmpqrstuvwxyzabcdefghjkmpqrstuvwxyz]{8})",
    flags=re.IGNORECASE,
)


class RorError(UrlError):
    """An error validating a ROR identifier, raised by Pydantic."""

    code = "ror"
    msg_template = "invalid ROR"


class Ror(HttpUrl):
    """A ROR (Research Organization Registry) type for Pydantic validation."""

    allowed_schemes = {"https"}

    @classmethod
    def __get_validators__(cls) -> Generator[AnyCallable, None, None]:
        yield cls.validate

    @classmethod
    def validate(
        cls, value: Any, field: ModelField, config: BaseConfig
    ) -> Ror:
        if value.__class__ == cls:
            return value

        m = ROR_PATTERN.search(value)
        if not m:
            raise RorError()

        identifier = m["identifier"]
        try:
            base32.decode(identifier, checksum=True)
        except ValueError:
            raise RorError()

        return HttpUrl.validate(value, field, config)
