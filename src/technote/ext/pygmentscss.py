"""A build-finished Sphinx hook that overwrites the ppygments.css file."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from pygments.formatters import HtmlFormatter
from sphinx.application import Sphinx

__all__ = ["overwrite_pygments_css"]


def overwrite_pygments_css(
    app: Sphinx, exceptions: Exception | None = None
) -> None:
    """Overwrite the pygments CSS file with a version that enables toggling
    between light and dark themes.

    Each selector is prefixed with html[data-theme='light|dark'] to enable
    toggling between light and dark themes with JavaScript.

    This approach is heavily based on pydata-sphinx-theme and furo:

    - https://github.com/pydata/pydata-sphinx-theme/blob/main/src/pydata_sphinx_theme/pygment.py
    - https://github.com/pradyunsg/furo/blob/main/src/furo/__init__.py
    """
    if exceptions:
        return

    pygment_css_path = Path(app.builder.outdir) / "_static" / "pygments.css"
    if not pygment_css_path.is_file():
        # Handles cases where the html builder isn't running (e.g. link check)
        return
    pygments_css = _create_pygments_css()
    pygment_css_path.write_text(pygments_css)


def _create_pygments_css() -> str:
    """Create the pygments CSS file that provides both light and dark themes.

    Returns
    -------
    str
        The custom pygments CSS contents.
    """
    # These Pygments styles are provided via
    # https://pypi.org/project/accessible-pygments/
    light_formatter = HtmlFormatter(style="github-light-high-contrast")
    dark_formatter = HtmlFormatter(style="github-dark-high-contrast")

    css_lines: list[str] = []
    css_lines.extend(_format_css(light_formatter, "light"))
    css_lines.extend(_format_css(dark_formatter, "dark"))

    return "\n".join(css_lines) + "\n"


def _format_css(formatter: HtmlFormatter, theme: str) -> Iterator[str]:
    """Format pygments CSS for a given theme.

    Parameters
    ----------
    formatter : HtmlFormatter
        The Pygments formatter to use (which defines the theme).
    theme : str
        The theme name (light or dark). This sets the html[data-theme]
        selector.

    Yields
    ------
    str
        A line of CSS for each selector.
    """
    selector_prefix = f"html[data-theme='{theme}'] .highlight"
    for line in formatter.get_linenos_style_defs():
        yield f"{selector_prefix} {line}"
    yield from formatter.get_background_style_defs(selector_prefix)
    yield from formatter.get_token_style_defs(selector_prefix)
