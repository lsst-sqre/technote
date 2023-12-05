"""Sphinx configuration for technotes.

To use this configuration in a Technote project, write a conf.py containing::

    from technote.sphinxconf import *
"""

from __future__ import annotations

from typing import Any

from .main import TechnoteSphinxConfig

# Restrict to only Sphinx configurations
__all__ = [
    # Technote configuration
    "T",
    # SPHINX
    "project",
    "author",
    "exclude_patterns",
    "html_theme",
    "extensions",
    "source_suffix",
    "nitpicky",
    "nitpick_ignore",
    "nitpick_ignore_regex",
    "numfig",
    # INTERSPHINX
    "intersphinx_mapping",
    "intersphinx_timeout",
    "intersphinx_cache_limit",
    # LINKCHECK
    "linkcheck_retries",
    "linkcheck_timeout",
    "linkcheck_ignore",
    # HTML
    "html_context",
    "html_baseurl",
    "html_domain_indices",
    "html_use_index",
    "html_permalinks_icon",
    # MYST
    "myst_enable_extensions",
]

T = TechnoteSphinxConfig.load()

# ============================================================================
# SPHINX General sphinx settings
# ============================================================================

project = T.title or ""
author = T.author or ""
exclude_patterns = [
    "_build",
    ".technote",
    ".github",
    ".tox",
    ".nox",
    "venv",
    ".venv",
    "README.rst",
    "README.md",
    "Makefile",
    "tox.ini",
    "requirements.txt",
    ".pre-commit-config.yaml",
    "technote.toml",
]
html_theme = "technote"

extensions: list[str] = [
    "myst_parser",
    "sphinx.ext.intersphinx",
    "technote.ext",
]
T.append_extensions(extensions)

# Add support for both Markdown and reStructuredText sources
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Nitpicky settings and ignored errors
nitpicky = T.nitpicky

nitpick_ignore: list[tuple[str, str]] = []
T.append_nitpick_ignore(nitpick_ignore)

nitpick_ignore_regex: list[tuple[str, str]] = []
T.append_nitpick_ignore_regex(nitpick_ignore_regex)

# Number figures and tables with captions
numfig = True

# ============================================================================
# INTERSPHINX Intersphinx settings
# ============================================================================

intersphinx_mapping: dict[str, tuple[str, str | None]] = {}
T.extend_intersphinx_mapping(intersphinx_mapping)

intersphinx_timeout = 10.0  # seconds

intersphinx_cache_limit = 5  # days


# ============================================================================
# LINKCHECK Link check builder settings
# ============================================================================

linkcheck_retries = 2
linkcheck_timeout = 15
linkcheck_ignore: list[str] = []
T.append_linkcheck_ignore(linkcheck_ignore)

# ============================================================================
# HTML HTML builder settings
# ============================================================================

html_context: dict[str, Any] = {"technote": T.jinja_context}

if T.toml.technote.canonical_url:
    html_baseurl = str(T.toml.technote.canonical_url)
else:
    html_baseurl = ""

html_domain_indices = False
html_use_index = False
html_permalinks_icon = "#"

# ============================================================================
# #MYST MyST markdown configurations
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
# ============================================================================

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
