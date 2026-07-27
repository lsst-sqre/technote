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
