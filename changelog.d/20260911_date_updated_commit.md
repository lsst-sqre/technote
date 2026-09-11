### Backwards-incompatible changes

- When `[technote] date_updated` is not set in `technote.toml`, the default is now the committer date of the checked-out git commit rather than the build clock. Pushing a commit and having CI build it is how a technote is published, so the commit's date is the publication date, and it is reproducible: rebuilding the same commit no longer re-dates the technote. The `SOURCE_DATE_EPOCH` environment variable is set, it takes precedence over git (the same reproducible-builds convention that Sphinx already follows).
