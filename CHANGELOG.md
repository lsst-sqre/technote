# Change log

<!-- scriv-insert-here -->

<a id='changelog-0.7.0'></a>
## 0.7.0 (2024-01-30)

### New features

- When the `technote.date_updated` field in `technote.toml` is not set, the update date internally defaults to "now" (the build time). This ensures that documents always carry some form of metadata about when they were modified.

- Code samples without captions (unwrapped `.highlight` divs) now have borders and are protected against x-overflow. This matches the behavior of code samples with captions.
- All code samples have negative left margin equal to their content padding so that the code lines up with the text column.
- The content (`div.sb-container`) now has bottom margin to give content breathing room.

<a id='changelog-0.6.2'></a>
## 0.6.2 (2023-12-14)

### Bug fixes

- Fix the `technote.ext.pygmentsscss` extension to handle cases where the HTML builder isn't being run.

<a id='changelog-0.6.1'></a>
## 0.6.1 (2023-12-14)

### Bug fixes

- The `technote.ext.wraptables` and `technote.ext.insertposttitles` extensions now gracefully handle cases when an `index.html` file does not exist. A reason for this might be that the build is running through the linkcheck builder.

<a id='changelog-0.6.0'></a>
## 0.6.0 (2023-12-05)

### New features

- Add `#svg-octicon-versions-16` to the `octicons.html` sprite template. This icon is useful for linking to alternative versions of a technote.

- Add `#svg-octicon-mortar-board-16` to the `octicons.html` sprite template. This icon is useful for linking to the document's citation.

- Export a variable, `T` from `technote.sphinxconf` that is an instance of `technote.main.TechnoteSphinxConfig`. This is useful for organizations that need to access the technote configuration and metadata in their own technote theme.

- Figures and tables with captions are now numbered using the Sphinx `numfig` configuration. Authors can reference figures by number using the `numref` role pointing to the figure's `name` option.

- Authors are now listed below the title of the technote. This is a change from the previous behavior of listing authors in the sidebar.

### Bug fixes

- Fix the `sidebar-authors.html` component template so that extra spaces aren't introduced between authors and commas.

<a id='changelog-0.5.1'></a>
## 0.5.1 (2023-11-29)

### Bug fixes

- Add `sphinx.ext.intersphinx` to the `extensions` list in `technote.sphinxconf`. This extension is required to use the `[technote.sphinx.intersphinx]` configuration.

<a id='changelog-0.5.0'></a>
## 0.5.0 (2023-11-28)

### Backwards-incompatible changes

- New structure for the `PersonName` model (used for the name key in  `[[technote.authors]]`):

  - Delete the `name` key to require structured names
  - Rename the `given_names` and `family_names` keys to `given` and `family`, respectively, which works better in context.

### New features

- Add a new `organization` key to the `[technote]` table to capture information about the organization publishing the technote series.

### Bug fixes

- The edit-on-GitHub link created in the Jinja context now correctly points to `index.md` if appropriate. Previously it assumed that the source page would be `index.rst`.

- Allow the `date_created`` and `date_created` keys in the `[technote]` table to use native TOML date formats (e.g., `2023-11-20T14:40:22Z`, without quoting as a string).

<a id='changelog-0.4.0'></a>
## 0.4.0 (2023-10-31)

### New features

- Added the [myst-parser](https://myst-parser.readthedocs.io/en/latest/) to the technote extension set. This allows Markdown files to be included in the technote build.

### Bug fixes

- Images added with a plain `.. image::` directive are now constrained to a maximum size of the container width. This is the same behavior as figures.

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
