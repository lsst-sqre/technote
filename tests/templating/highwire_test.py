"""Tests for the technote.templating.highwire module."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

from technote.metadata.model import (
    Organization,
    Person,
    Status,
    StructuredName,
    TechnoteMetadata,
    TechnoteState,
)
from technote.templating.dublincore import DublinCoreMetadata
from technote.templating.highwire import HighwireMetadata


def make_metadata(**kwargs: object) -> TechnoteMetadata:
    """Create a TechnoteMetadata with defaults that tests can override."""
    defaults: dict[str, object] = {
        "title": "Metadata test document",
        "status": Status(state=TechnoteState.stable, note=None),
        "canonical_url": "https://test-000.example.com/",
        "id": "TEST-000",
        "version": "1.0.0",
        "date_created": datetime(2023, 9, 1, tzinfo=UTC),
        "date_updated": datetime(2023, 9, 19, tzinfo=UTC),
        "authors": [
            Person(
                name=StructuredName(family="Sick", given="Jonathan"),
                orcid="https://orcid.org/0000-0003-3001-676X",
                email="jsick@example.com",
                affiliations=[
                    Organization(
                        name="Rubin Observatory",
                        ror="https://ror.org/048g3cy84",
                    )
                ],
            )
        ],
        "abstract_plain": "An abstract.",
    }
    defaults.update(kwargs)
    return TechnoteMetadata(**defaults)  # type: ignore[arg-type]


def test_author_institution() -> None:
    """A named affiliation becomes a citation_author_institution tag."""
    metadata = make_metadata()
    tags = HighwireMetadata(metadata=metadata).author_info

    assert (
        '<meta name="citation_author_institution" '
        'content="Rubin Observatory" data-highwire="true">' in tags
    )


def test_author_institution_without_name() -> None:
    """An affiliation identified only by its ROR emits no institution tag.

    The metadata factory sets the organization's name to an empty string when
    ``technote.toml`` identifies an affiliation only by its ``ror``. An empty
    ``citation_author_institution`` tag would be read by indexers (such as
    Google Scholar) as an empty institution, so no tag is emitted at all.
    """
    metadata = make_metadata(
        authors=[
            Person(
                name=StructuredName(family="Sick", given="Jonathan"),
                affiliations=[
                    Organization(name="", ror="https://ror.org/048g3cy84")
                ],
            )
        ]
    )
    tags = HighwireMetadata(metadata=metadata).author_info

    assert tags == [
        '<meta name="citation_author" content="Jonathan Sick" '
        'data-highwire="true">'
    ]
    assert "citation_author_institution" not in "\n".join(tags)


def test_citation_date_is_utc_normalized() -> None:
    """The citation_date is normalized to UTC, so it agrees with the date
    that the Dublin Core tags report for the same metadata.
    """
    # 2023-09-19T23:00-05:00 is 2023-09-20 in UTC.
    date_created = datetime(
        2023, 9, 19, 23, 0, tzinfo=timezone(timedelta(hours=-5))
    )
    metadata = make_metadata(date_created=date_created, date_updated=None)

    highwire_date = HighwireMetadata(metadata=metadata).date
    dublincore_html = DublinCoreMetadata(metadata=metadata).as_html()

    assert highwire_date == (
        '<meta name="citation_date" content="2023/09/20" '
        'data-highwire="true">'
    )
    assert '<meta name="DC.date" content="2023-09-20" >' in dublincore_html
