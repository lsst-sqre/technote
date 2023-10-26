# Change log

<!-- scriv-insert-here -->

<a id='changelog-0.3.0'></a>
## 0.3.0 (2023-10-26)

### Backwards-incompatible changes

- Require Pydantic 2 and later

- Require Python 3.11 and later

- The `technote.status` field is changed. The "planning" and "active" states are now "draft." The values in the `supersceding_urls` array are now tables with `url` and `title` (optional) keys.

- The metadata for creation and update dates are now maintained as full datetime objects rather than date objects.

- Refactor the original `technote.config` module into separate modules and classes for modeling `technote.toml` settings, internal representation of metadata (`technote.metadata.model.TechnoteMetadata`), the front-end for bootstrapping the Sphinx configuration in `conf.py` (`technote.main.TechnoteSphinxConfig`), and the Jinja context for HTML templating (`technote.templating.context.TechnoteJinjaContext`). A new factory class is responsible for creating these objects (`technote.factory.TechnoteFactory`). The benefit of this architecture is that it's not possible to continue building metadata from additional sources (external APIs and the technote context) since the metadata is not longer strictly tied to the `technote.toml` file representation.

### New features

- Light and dark colour themes are now set via a `html[data-theme='light']` or `dark` data theme attribute. JavaScript sets this element based on the user preference of 'light', 'dark', or 'auto' (using media queries for system settings). New CSS classes `technote-themed-light` and `technote-themed-dark` now determine what elements appear, or not, in certain themed contexts. This mechanism is highly inspired by pydata-sphinx-theme.
- Pygments highlighting CSS is now applied to all code samples, with light and dark themes using the mechanism described above. The default pygments styling comes from the `accessible-pygments` package. The mechanism for setting a light and dark Pygments theme is also based on pydata-sphinx-theme.
- New CSS custom properties for setting light and dark responsive colours.

- Include common metadata in the technote HTML:

  - Standard HTML meta tags like `description` and `canonical` URL link rel.
  - Highwire Press meta tags (used by Google Scholar)
  - OpenGraph meta tags (used by social media and messaging apps)
  - microformats2 annotations on relevant elements
  - Custom data attributes on relevant elements (the link to the technote source repository)

- Improve styling of the local table of contents. The outline is now sticky to the document and is independently scrollable if longer than the viewport.
- The content in the primary (left) sidebar is also sticky to the document and is independently scrollable if longer than the viewport.

- Improved styling:

  - Style the permalink icon
  - Style code blocks
  - Style admonitions
  - Style the metadata in the sidebars
  - Style footnotes
  - Style citations
  - Style quotes
  - Style tables and add a `wraptables`` Sphinx extension (included with the technote extension set) that wraps table elements in a `figure` to ensure wide tables have horizontal scrollbars
  - Improve layout in the mobile view

- The new "insertstatus" Sphinx extension, included in the `technote.ext` Sphinx extension, inserts an aside element below the title of the technote describing the status. The status is only published for non-stable states.

- Ignore common infrastructure directories and files from the Sphinx build.

### Bug fixes

- The `technote.ext.toc` extension now correctly handles the case where a technote has no sections.

### Other changes

- Adopt Ruff for linting

## 0.2.0 (2022-12-05)

This version adds customized Jinja templates as well as CSS to implement the core technote reading experience on the web.
This version includes an `abstract` reStructuredText directive, as well as a customized table of contents context variable for Jinja (`technote_toc`).

## 0.1.0 (2022-10-21)

First release of technote.
