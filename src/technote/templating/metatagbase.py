"""Support for generating HTML meta tags."""

from __future__ import annotations

from abc import ABC, abstractmethod


class MetaTagFormatterBase(ABC):
    """A base class for generating HTML meta tags."""

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
