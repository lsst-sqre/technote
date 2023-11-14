"""Technote configuration models (for technote.toml).

technote.toml is used both for setting document metadata and also configuring
the Sphinx build. Users of Technote can also add tables to technote.toml
to support their technote plugins and build infrastructure.
"""

from __future__ import annotations

import re
from collections.abc import MutableMapping
from dataclasses import dataclass
from pathlib import Path

from .factory import Factory
from .metadata.model import TechnoteMetadata
from .sources.tomlsettings import TechnoteToml
from .templating.context import TechnoteJinjaContext

__all__ = [
    "TechnoteSphinxConfig",
]


WHITESPACE_PATTERN = re.compile(r"\s+")


@dataclass
class TechnoteSphinxConfig:
    """A class that configures Sphinx in ``conf.py`` to build a technote."""

    factory: Factory

    toml: TechnoteToml
    """The parse ``technote.toml`` file."""

    metadata: TechnoteMetadata
    """The metadata for the technote.

    This metadata is principally obtained from the ``technote.toml`` settings
    file, but is augmented from content within the technote itself and from
    external sources.
    """

    root_filename: Path
    """Path to the root content document.

    Typically either ``index.md``, ``index.rst``, or ``index.ipynb``.
    """

    @classmethod
    def load(cls) -> TechnoteSphinxConfig:
        """Create a TechnoteSphinxConfig from the current directory."""
        factory = Factory()
        toml_settings = factory.find_and_load_toml()
        metadata = factory.load_metadata()

        _root_file_options = [
            Path("index.rst"),
            Path("index.md"),
            Path("index.ipynb"),
        ]
        _root_file = None
        for _root_file_candidate in _root_file_options:
            if _root_file_candidate.exists():
                _root_file = _root_file_candidate
                break
        if _root_file is None:
            raise RuntimeError(
                "Could not find root file. Is index.rst or index.md missing?"
            )

        return cls(
            factory=factory,
            toml=toml_settings,
            metadata=metadata,
            root_filename=_root_file,
        )

    @property
    def title(self) -> str | None:
        """The title of the document set via technote.toml metadata, or
        None if the document's H1 should be used.
        """
        return self.toml.technote.title

    @property
    def author(self) -> str:
        """A plaintext expression of the author or authors."""
        if self.metadata.authors:
            return ", ".join(
                a.name.plain_text_name for a in self.metadata.authors
            )
        else:
            return ""

    def append_extensions(self, extensions: list[str]) -> None:
        """Append user-configured extensions to an existing list."""
        for new_ext in self.toml.technote.sphinx.extensions:
            if new_ext not in extensions:
                extensions.append(new_ext)

    def extend_intersphinx_mapping(
        self, mapping: MutableMapping[str, tuple[str, str | None]]
    ) -> None:
        """Extend the ``intersphinx_mapping`` dictionary with configured
        projects.
        """
        for (
            project,
            url,
        ) in self.toml.technote.sphinx.intersphinx.projects.items():
            mapping[project] = (str(url), None)

    def append_linkcheck_ignore(self, link_patterns: list[str]) -> None:
        """Append URL patterns for sphinx.linkcheck.ignore to existing
        patterns.
        """
        link_patterns.extend(self.toml.technote.sphinx.linkcheck.ignore)

    def append_nitpick_ignore(
        self, nitpick_ignore: list[tuple[str, str]]
    ) -> None:
        """Append ``nitpick_ignore`` items from sphinx.nitpick_ignore."""
        nitpick_ignore.extend(self.toml.technote.sphinx.nitpick_ignore)

    def append_nitpick_ignore_regex(
        self, nitpick_ignore_regex: list[tuple[str, str]]
    ) -> None:
        """Append ``nitpick_ignore_regex`` items from sphinx.nitpick_ignore."""
        nitpick_ignore_regex.extend(
            self.toml.technote.sphinx.nitpick_ignore_regex
        )

    @property
    def nitpicky(self) -> bool:
        """The nitpicky boolean flag."""
        return self.toml.technote.sphinx.nitpicky

    @property
    def jinja_context(self) -> TechnoteJinjaContext:
        """The TechnoteJinjaContext that provides metadata to the HTML
        templates.
        """
        return self.factory.create_jinja_context(
            metadata=self.metadata, root_filename=self.root_filename
        )
