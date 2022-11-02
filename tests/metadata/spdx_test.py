"""Test the technote.metadata.spdx module."""

from __future__ import annotations

from technote.metadata.spdx import Licenses, SpdxFile, SpdxLicense


def test_spdxfile() -> None:
    """Test that SpdxFile can load licenses.json from the package."""
    spdx_file = SpdxFile.load_internal()
    assert isinstance(spdx_file, SpdxFile)


def test_cc_by() -> None:
    """Test reading the ``CC-BY-4.0`` license."""
    licenses = Licenses.load()
    spdx_id = "CC-BY-4.0"
    assert spdx_id in licenses
    license = licenses[spdx_id]
    assert isinstance(license, SpdxLicense)
    assert license.name == "Creative Commons Attribution 4.0 International"
    assert license.see_also[0] == (
        "https://creativecommons.org/licenses/by/4.0/legalcode"
    )
