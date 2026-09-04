### Backwards-incompatible changes

- The Highwire date tag is now emitted as `citation_publication_date` rather than `citation_date`. Google Scholar's inclusion guidelines document the tag as `citation_publication_date`; both spellings are accepted by Google Scholar and by Zotero's embedded-metadata translator, but the documented name is the safer long-term choice and matches the tag Documenteer emits for user guides. The value format (`YYYY/MM/DD`, in UTC) is unchanged.
