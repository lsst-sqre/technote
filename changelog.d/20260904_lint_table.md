### New features

- New `[technote.lint]` table in `technote.toml`, modelled by `technote.sources.tomlsettings.LintTable` and available as `TechnoteTable.lint`. Its `ignore` array lists codes of lint rules that a linting tool should skip for the technote. A rule code is an uppercase prefix naming the rule set followed by a number (such as `"TN105"` or `"R101"`); technote validates only that shape. Technote itself does not run lint rules; the table is owned here so that tools such as Documenteer's `technote lint` command read the same configuration from the parsed `technote.toml` model.
