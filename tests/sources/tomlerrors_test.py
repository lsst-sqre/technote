"""Tests for the technote.sources.tomlerrors module."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from technote.sources.tomlerrors import format_validation_error
from technote.sources.tomlsettings import TechnoteToml

PYDANTIC_FRAME = (
    "validation error",
    "Value error,",
    "input_value",
    "errors.pydantic.dev",
    "For further information",
)
"""Fragments of pydantic's own rendering of a `~pydantic.ValidationError`.

The model is technote's implementation detail, so none of these belong in
front of an author who wrote a ``technote.toml``.
"""


def report(toml_content: str) -> str:
    """Validate a ``technote.toml`` that must fail, and report the failure
    the way `~technote.factory.Factory.parse_toml` does.
    """
    with pytest.raises(ValidationError) as exc_info:
        TechnoteToml.parse_toml(toml_content)
    message = format_validation_error(
        exc_info.value, root=TechnoteToml, source="technote.toml"
    )
    assert_no_pydantic_frame(message)
    return message


def assert_no_pydantic_frame(message: str) -> None:
    """Assert that none of pydantic's own rendering reaches the author."""
    for fragment in PYDANTIC_FRAME:
        assert fragment not in message, message


def test_error_addresses_a_nested_table() -> None:
    """A rule code rejected by a validator names the table it is written in
    and the field, and is stated in the validator's own sentence.

    The validator runs on the whole list, so the address stops at the field
    rather than naming a position within it.
    """
    message = report('[technote]\n[technote.lint]\nignore=["tn105"]\n')

    assert message.startswith("Configuration error in technote.toml:")
    assert "[technote.lint] ignore" in message
    assert "Not a lint rule code ('tn105')." in message


def test_error_addresses_a_field_of_the_root_table() -> None:
    """A DOI that is not a DOI names the root table and the field."""
    message = report('[technote]\ndoi="10.71929"\n')

    assert "[technote] doi" in message
    assert "Not a DOI (10.71929)." in message


def test_error_reports_an_unquoted_value() -> None:
    """A DOI written unquoted is a float to TOML, and is reported by the
    same validator rather than as a type error about the model.
    """
    message = report("[technote]\ndoi=10.5\n")

    assert "[technote] doi" in message
    assert "Not a DOI (10.5)." in message


def test_error_addresses_an_array_of_tables() -> None:
    """A field missing from an author names the array of tables, the
    position of the author counted from one, the table within it, and the
    field.
    """
    message = report('[technote]\n[[technote.authors]]\nname.family="Sick"\n')

    assert "[[technote.authors]] author #1, name, field given" in message
    assert "Field required" in message


def test_error_addresses_an_array_nested_in_an_entry() -> None:
    """An error about a whole affiliation is addressed by both positions,
    each counted from one and named for what the array holds.
    """
    message = report(
        "[technote]\n"
        "[[technote.authors]]\n"
        'name.family="Sick"\n'
        'name.given="Jonathan"\n'
        'affiliations=[{address="x"}]\n'
    )

    assert "[[technote.authors]] author #1, affiliation #1" in message
    assert "An organization must have a name, ror, or internal_id" in message


def test_error_addresses_a_field_of_an_entry() -> None:
    """A field of an author rejected by a validator names the author and the
    field.
    """
    message = report(
        "[technote]\n"
        "[[technote.authors]]\n"
        'name.family="Sick"\n'
        'name.given="Jonathan"\n'
        'orcid="0000-0000"\n'
    )

    assert "[[technote.authors]] author #1, field orcid" in message
    assert "Not an ORCiD identifier checksum" in message


def test_error_addresses_an_inline_table() -> None:
    """A table written inline is addressed as the table it is, since that is
    where the author can also write it.
    """
    message = report('[technote]\nlicense={id="NOPE"}\n')

    assert "[technote.license] id" in message
    assert "not a valid SPDX license identifier" in message


def test_error_reports_a_value_outside_a_vocabulary() -> None:
    """A value outside a controlled vocabulary is reported with pydantic's
    own listing of the vocabulary, under an address in the file's terms.
    """
    message = report('[technote]\nstatus={state="bogus"}\n')

    vocabulary = "Input should be 'draft', 'stable', 'deprecated' or 'other'"
    assert "[technote.status] state" in message
    assert vocabulary in message


def test_error_addresses_a_key_of_a_mapping() -> None:
    """A key of a mapping is written in a table of its own, so it is
    addressed as a key in that table rather than as an index into anything.
    """
    message = report(
        "[technote]\n"
        "[technote.sphinx.intersphinx]\n"
        'projects={python="not a url"}\n'
    )

    assert "[technote.sphinx.intersphinx.projects] python" in message
    assert "Input should be a valid URL" in message


def test_error_reports_a_type_error() -> None:
    """A value pydantic rejects on its own is reported with pydantic's own
    sentence, under an address written in the file's vocabulary.
    """
    message = report("[technote]\ntitle=3\n")

    assert "[technote] title" in message
    assert "Input should be a valid string" in message


def test_error_names_a_missing_table() -> None:
    """A file without the root table names the table that is missing."""
    message = report("x=1\n")

    assert "[technote]" in message
    assert "Field required" in message


def test_error_names_no_model_when_a_table_is_not_one() -> None:
    """A table written as something other than a table is reported in TOML's
    vocabulary, since the model standing behind the table is not what the
    author wrote and not what they can fix.
    """
    message = report("technote=3\n")

    assert "[technote]" in message
    assert "should be a table" in message
    assert "TechnoteTable" not in message


def test_error_numbers_several_problems() -> None:
    """A file with more than one problem reports them all at once, numbered
    and counted, so the author fixes them in one pass rather than one build
    each.
    """
    message = report('[technote]\ntitle=3\ndoi="bad"\n')

    assert message.startswith("2 configuration errors in technote.toml:")
    assert "1. [technote] doi" in message
    assert "2. [technote] title" in message
    assert "Input should be a valid string" in message
    assert "Not a DOI (bad)." in message
