"""Tests for what a build prints when technote.toml does not validate.

The claim under test is about the console: an author who mistypes a value in
:file:`technote.toml` must be able to read what is wrong with it from the
build's own output. That is a property of the process, not of the exception,
so the build runs in a subprocess and the assertions are made against what it
wrote to stdout and stderr.

Sphinx renders every `~sphinx.errors.SphinxError` raised while :file:`conf.py`
runs inside its own crash frame -- a "Configuration error!" banner, a
saved-traceback path, and an invitation to report the problem to sphinx-doc.
That frame is Sphinx's, printed unconditionally, so it is not asserted
against here; what matters is that technote's message is inside it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CONF_PY = "from technote.sphinxconf import *\n"

INDEX_RST = """
##############
Example title
##############

Body text.
"""

TECHNOTE_TOML = """
[technote]
id = "SQR-000"
series_id = "SQR"
canonical_url = "https://sqr-000.lsst.io/"
github_url = "https://github.com/lsst-sqre/sqr-000"

[technote.lint]
ignore = ["tn105"]
"""


def test_build_reports_an_invalid_technote_toml(tmp_path: Path) -> None:
    root = tmp_path / "technote"
    root.mkdir()
    (root / "conf.py").write_text(CONF_PY)
    (root / "index.rst").write_text(INDEX_RST)
    (root / "technote.toml").write_text(TECHNOTE_TOML)

    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html", ".", "_build"],  # noqa: S603
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0, output
    assert "[technote.lint] ignore" in output
    assert "Not a lint rule code ('tn105')." in output
    assert "Syntax or validation issue" not in output
