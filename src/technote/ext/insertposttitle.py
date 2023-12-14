"""Inserts the status of the technote below thte h1."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape
from sphinx.application import Sphinx

from ..templating.context import TechnoteJinjaContext

__all__ = ["insert_post_title"]


def insert_post_title(app: Sphinx, exceptions: Exception | None) -> None:
    """Insert a html templates directly below the title.

    This extension adds the following HTML templates below the h1 section:

    - The status aside is only added for non-stable states (draft, deprecated,
      or other).
    """
    if exceptions:
        return

    try:
        technote_context = app.config.html_context["technote"]
    except (KeyError, AttributeError):
        return

    technote_context = cast(TechnoteJinjaContext, technote_context)

    # Load template from templates/status.html.jinja
    jinja_env = Environment(
        loader=PackageLoader("technote", "ext/templates"),
        autoescape=select_autoescape(["html"]),
    )
    template = jinja_env.get_template("post-title.html.jinja")
    status_html = template.render(technote=technote_context)
    status_soup = BeautifulSoup(status_html, "html.parser")

    # Insert the status aside into the technote
    html_path = Path(app.builder.outdir) / "index.html"
    if not html_path.is_file():
        return
    soup = BeautifulSoup(html_path.read_text(), "html.parser")
    title = soup.find("h1")
    title.insert_after(status_soup)
    html_path.write_text(str(soup))
