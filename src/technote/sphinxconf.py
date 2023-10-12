"""Sphinx configuration for technotes.

To use this configuration in a Technote project, write a conf.py containing::

    from technote.sphinxconf import *
"""

from __future__ import annotations

from typing import Any

from .main import TechnoteSphinxConfig

# Restrict to only Sphinx configurations
__all__ = [
    # SPHINX
    "project",
    "author",
    "exclude_patterns",
    "html_theme",
    "extensions",
    "nitpicky",
    "nitpick_ignore",
    "nitpick_ignore_regex",
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
]

_t = TechnoteSphinxConfig.load()

# ============================================================================
# SPHINX General sphinx settings
# ============================================================================

project = _t.title or ""
author = _t.author or ""
exclude_patterns = ["_build", "README.rst", "README.md", "Makefile"]
html_theme = "technote"

extensions: list[str] = ["technote.ext"]
_t.append_extensions(extensions)

# Nitpicky settings and ignored errors
nitpicky = _t.nitpicky

nitpick_ignore: list[tuple[str, str]] = []
_t.append_nitpick_ignore(nitpick_ignore)

nitpick_ignore_regex: list[tuple[str, str]] = []
_t.append_nitpick_ignore_regex(nitpick_ignore_regex)

# ============================================================================
# INTERSPHINX Intersphinx settings
# ============================================================================

intersphinx_mapping: dict[str, tuple[str, str | None]] = {}
_t.extend_intersphinx_mapping(intersphinx_mapping)

intersphinx_timeout = 10.0  # seconds

intersphinx_cache_limit = 5  # days


# ============================================================================
# LINKCHECK Link check builder settings
# ============================================================================

linkcheck_retries = 2
linkcheck_timeout = 15
linkcheck_ignore: list[str] = []
_t.append_linkcheck_ignore(linkcheck_ignore)

# ============================================================================
# HTML HTML builder settings
# ============================================================================

html_context: dict[str, Any] = {"technote": _t.jinja_context}

if _t.toml.technote.canonical_url:
    html_baseurl = str(_t.toml.technote.canonical_url)
else:
    html_baseurl = ""

html_domain_indices = False
html_use_index = False
html_permalinks_icon = "#"
