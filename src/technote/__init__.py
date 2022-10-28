"""Rubin Observatory's framework for Sphinx-based technote documents."""

__all__ = ["__version__", "setup"]

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Dict

from sphinx.application import Sphinx

__version__: str
"""The version string of technote (:pep:`440` compatible)."""

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"


def setup(app: Sphinx) -> Dict[str, Any]:
    """Sphinx entrypoint for technote.

    Parameters
    ----------
    app
        The Sphinx application setting up the technote theme.

    Returns
    -------
    dict
        The extension dictionary. Technote is parallel read and write safe.
        The extension version is the same as the package version,
        see `__version__`.
    """
    theme_path = Path(__file__).parent.joinpath("theme").resolve()
    app.add_html_theme("technote", str(theme_path))

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "version": __version__,
    }
