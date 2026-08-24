"""The DOI (Digital Object Identifier)."""

from __future__ import annotations

import re

__all__ = ["DOI_PATTERN", "DOI_PREFIXES", "normalize_doi"]


DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$")
"""Pattern for a bare DOI (the ``10.NNNN/suffix`` form)."""

DOI_PREFIXES = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
    "doi:",
)
"""Prefixes that are stripped when normalizing a DOI to its bare form."""

_WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_doi(value: str) -> str:
    """Normalize a DOI into its bare form, ``10.NNNN/suffix``.

    Parameters
    ----------
    value
        A DOI, either in its bare form or expressed as a ``doi.org`` URL or
        with a ``doi:`` prefix. Whitespace around the DOI, and between a
        prefix and the DOI, is ignored.

    Returns
    -------
    str
        The bare DOI.

    Raises
    ------
    ValueError
        Raised if the value is not a syntactically-valid DOI.
    """
    doi = _WHITESPACE_PATTERN.sub(" ", value).strip()
    for prefix in DOI_PREFIXES:
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix) :].strip()
            break
    if not DOI_PATTERN.match(doi):
        raise ValueError(
            f"Not a DOI ({value}). A DOI looks like 10.5281/zenodo.10385500, "
            "and may also be given as a https://doi.org/ URL."
        )
    return doi
