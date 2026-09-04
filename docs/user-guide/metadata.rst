##############################
Metadata published by technote
##############################

Technote publishes metadata with HTML documents.
This metadata can be used for a number of purposes, from search engine optimization, to inclusion in Google Scholar, unfurling in social media and message apps, and even for maintaining institutional documentation indices.
Technote uses supports a number of metadata standards, including Highwire Press, Open Graph, Dublin Core, schema.org (as JSON-LD), microformats2, and custom element annotations with data attributes.
This page describes the metadata that Technote publishes.

Standard HTML metadata
======================

Technote publishes standard HTML metadata:

- ``meta name="title"`` is the document's title (h1 heading).
- ``meta name="description"`` is the document's description derived from the ``abstract`` directive.
- ``meta name="generator"`` is the name of the software that generated the document. Example: ``<meta name="generator" content="technote 1.0.0: https://technote.lsst.io">``.
- ``link ref="canonical"`` is the canonical URL of the document, derived from the ``canonical_url`` field in a document's ``technote.toml`` configuration file.

Highwire Press metadata
=======================

Google Scholar uses Highwire Press metadata to index literature.
Technote publishes the following ``meta`` tags:

- ``citation_title``
- ``citation_author``
- ``citation_author_institution``
- ``citation_author_email``
- ``citation_author_orcid``
- ``citation_publication_date``
- ``citation_doi`` (from the :ref:`doi <toml-technote-doi>` field)
- ``citation_technical_report_number``
- ``citation_fulltext_html_url``

OpenGraph metadata
==================

Social media and messaging apps use OpenGraph metadata to unfurl links.
Technote publishes the following ``meta`` tags:

- ``og:title``
- ``og:description``
- ``og:url``
- ``og:type`` (always ``article``)
- ``og:article:author``
- ``og:article:published_time``
- ``og:article:modified_time``

Dublin Core metadata
====================

Dublin Core is a general-purpose bibliographic vocabulary that repository software and metadata harvesters understand.
Technote publishes the following ``meta`` tags:

- ``DC.title``
- ``DC.creator`` (one per author)
- ``DC.description`` (the abstract)
- ``DC.identifier`` (the technote's DOI as a ``https://doi.org`` URL, falling back to the canonical URL when the technote has no DOI)
- ``DC.date`` (the creation date, falling back to the updated date)
- ``DC.publisher`` (from the :ref:`organization <toml-technote-organization>` field)
- ``DC.type`` (always ``Text``)
- ``DC.format`` (always ``text/html``)
- ``DC.language`` (always ``en``)
- ``DC.rights`` (the SPDX license identifier)

schema.org metadata
===================

Technote publishes a `schema.org <https://schema.org>`__ description of the document as a JSON-LD block in the HTML head (a ``script`` element with ``type="application/ld+json"``).
Search engines and DOI infrastructure use this structured data to understand the page.

The technote is described as a `Report <https://schema.org/Report>`__ with these properties, when the corresponding metadata is available:

- ``@id`` (the DOI as a ``https://doi.org`` URL, falling back to the canonical URL)
- ``identifier`` (a ``PropertyValue`` carrying the DOI, following the DataCite-to-schema.org crosswalk)
- ``name``, ``url``, ``abstract``, and ``description``
- ``reportNumber`` (the technote's :ref:`id <toml-technote-id>`) and ``version``
- ``datePublished`` and ``dateModified``
- ``author`` (with ORCiD as ``@id``, email, and affiliations)
- ``publisher`` (from the :ref:`organization <toml-technote-organization>` field, with its ROR as ``@id``)
- ``license`` (the URL for the SPDX license identifier)
- ``inLanguage`` (always ``en``)

microformats2 metadata
======================

microformats2 is a standard for annotating HTML element that reflect standard document metadata.
The annotations are published as ``class`` attributes on HTML elements.

- ``h-entry`` is applied to the container element for the document (including sidebars).
- ``e-content`` is applied to the container element for the document's content.
- ``p-summary`` is applied to the abstract's container section.
- ``p-author`` is applied to the name of each author.
- ``dt-updated`` is applied to the date element of the last update.
- ``dt-published`` is applied to the date element of the original publication date.

Element data attributes
=======================

For on-page metadata that is not covered by the standards above, Technote annotates on-page metadata as data attributes on HTML elements.

- ``data-technote-source-url`` is set to the URL of the source repository for the document (e.g. on GitHub). This data attribute is applied to the ``a`` element that links to the source repository.
