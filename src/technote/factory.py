"""The factory creates classes based on configuration."""

from __future__ import annotations

__all__ = ["Factory"]

from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError
from sphinx.errors import ConfigError

from .metadata.model import (
    Link,
    Organization,
    Person,
    SourceRepository,
    Status,
    StructuredName,
    TechnoteMetadata,
    TechnoteState,
)
from .sources.tomlsettings import TechnoteToml
from .templating.context import TechnoteJinjaContext


class Factory:
    """A factory for creating classes based on configuration."""

    def __init__(self) -> None:
        self._toml: TechnoteToml | None = None  # cached toml settings

    def find_and_load_toml(self) -> TechnoteToml:
        if self._toml is not None:
            return self._toml

        path = Path("technote.toml")
        if not path.is_file():
            raise ConfigError("Cannot find the technote.toml file.")
        return self.parse_toml(path.read_text())

    def parse_toml(self, toml_content: str) -> TechnoteToml:
        """Parse the content of a ``technote.toml`` file."""
        try:
            parsed_toml = TechnoteToml.parse_toml(toml_content)
        except ValidationError as e:
            message = "Syntax or validation issue in technote.toml"
            raise ConfigError(message) from e
        self._toml = parsed_toml
        return self._toml

    def load_metadata(self) -> TechnoteMetadata:
        """Create the TechnoteMetadata."""
        # The TOML settings are the principle seed for the TechnoteMetadata
        toml_settings = self.find_and_load_toml()

        authors = [
            Person(
                name=StructuredName(
                    family=author.name.family,
                    given=author.name.given,
                ),
                email=author.email,
                orcid=str(author.orcid) if author.orcid else None,
                internal_id=author.internal_id,
                affiliations=[
                    Organization(
                        name=affiliation.name or "",  # TODO: resolve from ROR?
                        url=str(affiliation.url) if affiliation.url else None,
                        address=affiliation.address,
                        ror=str(affiliation.ror) if affiliation.ror else None,
                        internal_id=affiliation.internal_id,
                    )
                    for affiliation in author.affiliations
                ],
            )
            for author in toml_settings.technote.authors
        ]

        if toml_settings.technote.github_url is not None:
            source_repository = SourceRepository(
                url=str(toml_settings.technote.github_url),
                branch=toml_settings.technote.github_default_branch,
            )
        else:
            source_repository = None

        if toml_settings.technote.status is not None:
            status = Status(
                state=toml_settings.technote.status.state,
                note=toml_settings.technote.status.note,
                supersceding_urls=[
                    Link(url=str(link.url), title=link.title)
                    for link in toml_settings.technote.status.supersceding_urls
                ],
            )
        else:
            status = Status(
                state=TechnoteState.stable, note=None, supersceding_urls=[]
            )

        if toml_settings.technote.license is not None:
            license_id = toml_settings.technote.license.id
        else:
            license_id = None

        # Default the "date_updated" to now (build time) if it is not
        # hard-coded into the TOML file.
        date_updated = toml_settings.technote.date_updated_datetime
        if date_updated is None:
            date_updated = datetime.now(tz=UTC)

        return TechnoteMetadata(
            title=toml_settings.technote.title or "",
            canonical_url=(
                str(toml_settings.technote.canonical_url)
                if toml_settings.technote.canonical_url
                else None
            ),
            id=toml_settings.technote.id,
            series_id=toml_settings.technote.series_id,
            date_created=toml_settings.technote.date_created_datetime,
            date_updated=date_updated,
            version=toml_settings.technote.version,
            authors=authors,
            source_repository=source_repository,
            status=status,
            license_id=license_id,
        )

    def create_jinja_context(
        self, metadata: TechnoteMetadata, root_filename: Path
    ) -> TechnoteJinjaContext:
        """Create the Jinja context for the technote."""
        # We don't use a cached TechnoteMetadata because TechnoteSphinxConfig
        # or TechnoteJinjaContext may modify the metadata. We don't want to
        # own it in the factory.
        return TechnoteJinjaContext(
            metadata=metadata, root_filename=root_filename
        )
