"""The wraptables extension wraps HTML tables in figures."""

from __future__ import annotations

from bs4 import BeautifulSoup
from sphinx.application import Sphinx


def wrap_html_tables(app: Sphinx, exceptions: Exception | None = None) -> None:
    """Wrap the HTML tables in a figure tag.

    Having a wrapping element for a ``table`` in HTML allows us to constrain
    the width of the table and permit overflow scrolling. The alternative
    approach, setting the ``table`` to ``display: block`` loses the
    table's accessibility (see
    https://www.tpgi.com/short-note-on-what-css-display-properties-do-to-table-semantics/).
    """
    if exceptions:
        return

    # Assumes that technotes consist of only a single index.html file
    # by definition.
    html_path = app.builder.outdir / "index.html"

    soup = BeautifulSoup(html_path.read_text(), "html.parser")
    for table_element in soup.find_all("table"):
        figure = soup.new_tag("figure")
        figure.attrs["class"] = "technote-table"
        table_element.wrap(figure)

    html_path.write_text(str(soup))