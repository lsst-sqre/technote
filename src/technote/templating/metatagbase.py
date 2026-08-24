"""Support for generating HTML meta tags."""

from __future__ import annotations

import html
from abc import ABC, abstractmethod
from typing import ClassVar


class MetaTagFormatterBase(ABC):
    """A base class for generating HTML meta tags.

    Subclasses configure the shape of their tags with the
    `tag_name_attribute`, `tag_name_prefix`, and `extra_tag_attributes` class
    attributes, and then build individual tags with `_format_tag`. Routing all
    tag construction through `_format_tag` means that the ``content`` value is
    always escaped, so a subclass cannot accidentally emit an unescaped
    attribute.
    """

    tag_name_attribute: ClassVar[str] = "name"
    """The ``meta`` attribute that names the tag (``name`` or ``property``)."""

    tag_name_prefix: ClassVar[str] = ""
    """The prefix applied to each tag name (e.g. ``citation_``)."""

    extra_tag_attributes: ClassVar[dict[str, str]] = {}
    """Additional attributes included in every tag."""

    def __str__(self) -> str:
        """Create the Highwire metadata tags."""
        return self.as_html()

    @property
    @abstractmethod
    def tag_attributes(self) -> list[str]:
        """The names of class properties that create tags."""
        raise NotImplementedError

    def as_html(self) -> str:
        """Create the Highwire metadata HTML tags."""
        tags: list[str] = []
        for prop in self.tag_attributes:
            self.extend_not_none(tags, getattr(self, prop))
        return "\n".join(tags) + "\n"

    @staticmethod
    def extend_not_none(
        entries: list[str], new_item: None | str | list[str]
    ) -> None:
        """Extend a list with new items if they are not None."""
        if new_item is None:
            return
        if isinstance(new_item, str):
            entries.append(new_item)
        else:
            entries.extend(new_item)

    @staticmethod
    def escape_content(content: str) -> str:
        """Escape a string for use as the ``content`` of a ``meta`` tag."""
        return html.escape(content, quote=True)

    def _format_tag(self, name: str, content: str) -> str:
        """Format a ``meta`` tag, escaping the content."""
        tag_name = self.escape_content(f"{self.tag_name_prefix}{name}")
        extras = " ".join(
            f'{key}="{self.escape_content(value)}"'
            for key, value in self.extra_tag_attributes.items()
        )
        return (
            f'<meta {self.tag_name_attribute}="{tag_name}" '
            f'content="{self.escape_content(content)}" '
            f"{extras}>"
        )
