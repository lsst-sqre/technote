"""Pytest configuration and fixtures."""

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

pytest_plugins = ("sphinx.testing.fixtures",)

# Exclude 'roots' dirs for pytest test collector
collect_ignore: list[str] = ["roots"]


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "sphinx(builder, testroot='name'): Run sphinx on a site"
    )


@pytest.fixture(scope="session")
def rootdir() -> Path:
    """Directory containing Sphinx projects for testing (`str`)."""
    return Path(__file__).parent.resolve() / "roots"


@pytest.fixture(scope="session", autouse=True)
def _pin_source_date_epoch() -> Iterator[None]:
    """Pin ``SOURCE_DATE_EPOCH`` for the whole test session.

    When ``technote.toml`` does not declare ``date_updated``, technote derives
    it from the publication event: ``SOURCE_DATE_EPOCH`` if set, otherwise the
    committer date of the checked-out commit, otherwise the build clock.
    ``sphinx.testing`` copies each test root into a pytest temp directory that
    has no ``.git``, so without a pin every Sphinx build in the suite would
    shell out to ``git log``, be told it is not in a repository, and render the
    build clock into the technote's metadata. Pinning the variable makes that
    output deterministic and saves a subprocess per build.

    The value is the same ``1700000000`` (2023-11-14T22:13:20Z) that
    ``tests/metadata_test.py`` asserts on. Tests that need another branch of
    the resolution order override the variable themselves with a
    function-scoped ``monkeypatch``, which takes precedence over this fixture;
    see ``tests/metadata/builddate_test.py``.
    """
    # monkeypatch is function-scoped, so use a MonkeyPatch instance directly.
    mp = pytest.MonkeyPatch()
    mp.setenv("SOURCE_DATE_EPOCH", "1700000000")
    try:
        yield
    finally:
        mp.undo()


@pytest.fixture(autouse=True)
def _reset_sphinxconf_module() -> Iterator[None]:
    """Evict ``technote.sphinxconf`` from the module cache around each test.

    Test root ``conf.py`` files do ``from technote.sphinxconf import *``, and
    that module reads ``technote.toml`` from the working directory at import
    time. Python caches the module, so a second Sphinx build in the same
    process would otherwise reuse the *first* test root's settings. Real
    technote builds each get their own process; dropping the module keeps the
    test suite order-independent and matches that behaviour.
    """
    sys.modules.pop("technote.sphinxconf", None)
    yield
    sys.modules.pop("technote.sphinxconf", None)
