### Bug fixes

- When `[technote] title` is not set in `technote.toml`, the title taken from the document's H1 heading is now resolved at the end of Sphinx's read phase (the `env-updated` event) rather than only while the HTML builder writes pages. `TechnoteMetadata.title` is therefore correct for every builder, including `dummy` and `linkcheck`, and for tools that run a Sphinx read in-process to inspect the metadata. A title set in `technote.toml` still wins, and HTML output is unchanged.

### New features

- New `technote.ext.metadata.resolve_title` function that returns a document's title (the text of its first `title` node) from a doctree, for downstream code that already holds a doctree.
