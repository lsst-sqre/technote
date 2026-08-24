"""Tests for the technote.templating.metatagbase module."""

from __future__ import annotations

from typing import ClassVar

from technote.templating.metatagbase import MetaTagFormatterBase


class NameFormatter(MetaTagFormatterBase):
    """A formatter that uses the ``name`` attribute and no extras."""

    tag_name_prefix: ClassVar[str] = "DC."

    @property
    def tag_attributes(self) -> list[str]:
        return ["title"]

    @property
    def title(self) -> str:
        return self._format_tag("title", 'A "quoted" <title> & more')


class PropertyFormatter(MetaTagFormatterBase):
    """A formatter that uses the ``property`` attribute and extra
    attributes.
    """

    tag_name_attribute: ClassVar[str] = "property"
    tag_name_prefix: ClassVar[str] = "og:"
    extra_tag_attributes: ClassVar[dict[str, str]] = {"data-test": "true"}

    @property
    def tag_attributes(self) -> list[str]:
        return ["title"]

    @property
    def title(self) -> str:
        return self._format_tag("title", 'A "quoted" <title> & more')


def test_format_tag_escapes_content() -> None:
    """The base class escapes content so it cannot break out of the
    attribute.
    """
    assert NameFormatter().title == (
        '<meta name="DC.title" '
        'content="A &quot;quoted&quot; &lt;title&gt; &amp; more" >'
    )


def test_format_tag_with_extra_attributes() -> None:
    """Extra attributes are appended after the escaped content."""
    assert PropertyFormatter().title == (
        '<meta property="og:title" '
        'content="A &quot;quoted&quot; &lt;title&gt; &amp; more" '
        'data-test="true">'
    )


def test_as_html() -> None:
    """The rendered HTML is the newline-joined tags."""
    assert NameFormatter().as_html() == f"{NameFormatter().title}\n"
