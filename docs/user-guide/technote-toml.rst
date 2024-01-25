#######################
technote.toml reference
#######################

The :file:`technote.toml` file contains metadata about the technote, along with configuration options for the Sphinx build.
This page describes the schema for this file.

.. seealso::

   If you are not familiar with TOML, see the `TOML documentation <https://toml.io/en/v1.0.0>`_.

.. _toml-technote:

[technote]
==========

|required|

The ``[technote]`` table is the root table for technote metadata and configuration in the :file:`technote.toml` file.

.. _toml-technote-id:

id
--

|optional|

An internal identifier for the technote.

.. code-block:: toml

   [technote]
   id = "SQR-001"

.. see also::

   :ref:`toml-technote-series-id`

.. _toml-technote-series-id:

series_id
---------

|optional|

An internal identifier for a series or collection this technote belongs to.

.. code-block:: toml

   [technote]
   id = "SQR-001"
   series_id = "SQR"

.. see also::

   :ref:`toml-technote-id`

.. _toml-technote-organization:

organization
------------

|optional|

The organization that publishes the technote series.
The value is a table with the same structure as :ref:`toml-technote-authors-affiliations`.

.. _toml-technote-title:

title
-----

|optional|

The title of the technote.
Use this metadata field to override the title in the content.
Generally this metadata *should not* be set in :file:`technote.toml` if the document title in content file is correct.

.. _toml-technote-date-created:

date_created
------------

|optional|

Date and time when the technote was created.
This should be set as an :rfc:`3339` (i.e., ISO8601) string.
Either as a date (``YYYY-MM-DD``) or a date and time with a timezone (``YYYY-MM-DDTHH:MM:SSZ``).

TOML treats dates and date-times as native types, and therefore don't use quotes:

.. code-block:: toml

   [technote]
   date_created = 2023-01-01T00:00:00Z


.. _toml-technote-date-updated:

date_updated
------------

|optional|

Date and time when the technote was last updated.
This should be set as an ISO8601 string.
This should be set as an :rfc:`3339` (i.e., ISO8601) string.
Either as a date (``YYYY-MM-DD``) or a date and time with a timezone (``YYYY-MM-DDTHH:MM:SSZ``).

TOML treats dates and date-times as native types, and therefore don't use quotes:

.. code-block:: toml

   [technote]
   date_updated = 2023-01-01T00:00:00Z

.. _toml-technote-version:

version
-------

|optional|

The version of the technote.

.. _toml-technote-doi:

doi
---

|optional|

The most-relevant DOI that identifies this technote.
This can be a pre-registerered DOI (i.e. for Zenodo) so that the  DOI can be present in the released technote source.

.. _toml-technote-canonical-url:

canonical_url
-------------

|optional|

The URL where this technote is published.

.. _toml-technote-github-url:

github_url
----------

|optional|

The URL of the GitHub repository hosting this technote.

.. _toml-technote-github-default-branch:

github_default_branch
---------------------

|optional| Default: ``main``

The default branch of the GitHub repository.

.. _toml-technote-authors:

[[technote.authors]]
====================

Authors are specified as an array of tables.
In :file:`technote.toml`, this means that each author is described with their own ``[[technote.authors]]`` table.
You can have as many ``[[technote.authors]]`` tables as you need.

.. _toml-technote-authors-name:

name
----

|required|

The author's name, as it should appear in the technote:

.. code-block:: toml

   [[technote.authors]]
   name.given = "Vera"
   name.family = "Rubin"

.. _toml-technote-authors-internal-id:

internal_id
-----------

|optional|

An internal identifier for the person.
This can be used to associate an author with an organization's author database.

.. _toml-technote-authors-email:

email
-----

|optional|

The author's email address.

.. _toml-technote-authors-orcid:

orcid
-----

|optional|

The author's ORCiD identifier.
This should be specified as a full URL.

.. _toml-technote-authors-affiliations:

[[technote.authors.affiliations]]
=================================

|optional|

An author can have multiple affiliations.
Each affiliation is a table in the ``[[technote.authors.affiliations]]`` array.

.. code-block:: toml

   [technote.authors]
   name.given = "Vera C."
   name.family = "Rubin"
   affiliations = [
     { name = "Department of Astronomy, University of Washington" },
     { name = "Department of Terrestrial Magnetism, Carnegie Institution of Washington" }
   ]

The above example used inline tables for each affiliation.
If each affiliation has a large amount of metadata you can instead use the array of table TOML syntax:

.. code-block:: toml

   [technote.authors]
   name.given = "Vera C."
   name.family = "Rubin"
   [[technote.authors.affiliations]]
   name = "Department of Astronomy, University of Washington"
   [[technote.authors.affiliations]]
   name = "Department of Terrestrial Magnetism, Carnegie Institution of Washington"

.. _toml-technote-authors-affiliations-name:

name
----

|optional|

The name of the entity.

.. _toml-technote-authors-affiliations-internal-id:

internal_id
-----------

|optional|

An internal identifier for the entity.
This field can be used to an organization's database of affiliations.

.. _toml-technote-authors-affiliations-address:

address
-------

|optional|

The address of the entity.

.. _toml-technote-authors-affiliations-url:

url
---

|optional|

The homepage of the entity.

.. _toml-technote-authors-affiliations-ror:

ror
---

|optional|

The `ROR <https://ror.org>`__ identifier of the entity.
This should be specified as a full URL.
ROR is a *research organization registry* that provides a persistent identifier for research organizations, similar to ORCiD identifiers for individual researchers.

.. _toml-technote-contributors:

[[technote.contributors]]
=========================

|optional|

Besides authors, a technote can have other contributors such as reviewers, editors, and approvers.
The ``[[technote.contributors]]`` array of tables is structured identically to the ``[[technote.authors]]`` array of tables, with the addition of ``role`` and ``note`` keys.

.. _toml-technote-contributors-role:

role
----

|optional|

The role of the contributor.
This is an enumeration of one of the following values from the Zenodo schema:

- ``ContactPerson``
- ``DataCollector``
- ``DataCurator``
- ``DataManager``
- ``Distributor``
- ``Editor``
- ``Funder``
- ``HostingInstitution``
- ``Producer``
- ``ProjectLeader``
- ``ProjectManager``
- ``ProjectMember``
- ``RegistrationAgency``
- ``RegistrationAuthority``
- ``RelatedPerson``
- ``Researcher``
- ``ResearchGroup``
- ``RightsHolder``
- ``Supervisor``
- ``Sponsor``
- ``WorkPackageLeader``
- ``Other``

.. _toml-technote-contributors-note:

note
----

|optional|

A note describing the role of the contributor.
This is particularly useful if the role is "Other".

.. _toml-technote-status:

[technote.status]
=================

|optional|

A technote is an evolving document.
You can describe whether the technote is being actively drafted, stable, or deprecated with the ``[technote.status]`` table.

.. _toml-technote-status-state:

state
-----

|required|

The state of the technote is an enumeration with the following allowed values:

``draft``
    The technote is being actively drafted or is not in a complete state.

``stable``
    The technote is stable and complete.

``deprecated``
    The technote is deprecated and should not be used.

``other``
    The technote is in some other state. Use the ``note`` key to describe the state.

.. _toml-technote-status-note:

note
----

|optional|

A note describing the state of the technote.

.. _toml-technote-status-superseding-urls:

[[technote.status.superseding_urls]]
====================================

|optional|

A deprecated technote might be supersceded by other works.
Use this array of tables to describe those links

.. _toml-technote-status-superseding-urls-url:

url
---

|required|

The URL of the work that supersedes this technote.

.. _toml-technote-status-superseding-urls-title:

title
-----

|optional|

The title of the work that supersedes this technote.

.. _toml-technote-license:

[technote.license]
==================

|optional|

The license of the technote.

.. code-block:: toml

   [technote.license]
   id = "CC-BY-4.0"

.. _toml-technote-license-id:

id
--

|required|

The `SPDX identifier <https://spdx.org/licenses/>`__ of the license.

.. _toml-technote-sphinx:

[technote.sphinx]
=================

|optional|

You can specify many configurations for the Sphinx build in the ``[technote.sphinx]`` table.
Technote's Sphinx configuration module, ``technote.sphinxconf``, applies these values in the Sphinx :file:`conf.py` file.

.. _toml-technote-sphinx-extensions:

extensions
----------

|optional|

An array of Sphinx extensions to enable, equivalent to the ``extensions`` list in Sphinx's :file:`conf.py`.

.. _toml-technote-sphinx-nitpicky:

nitpicky
--------

|optional| Default: ``false``

Escalates build warnings to errors.

.. _toml-technote-sphinx-nitpick-ignore:

nitpick_ignore
--------------

|optional|

An array of two-item arrays specifying errors to ignore.
The first item is the type (such as a role like ``py:class``), and the second item is the target (such as a class name).

.. _toml-technote-sphinx-nitpick-ignore-regex:

nitpick_ignore_regex
--------------------

|optional|

Same as ``nitpick_ignore``, but items are interpreted as regular expressions.

.. _toml-technote-sphinx-intersphinx:

[technote.sphinx.intersphinx]
=============================

|optional|

Configurations for the ``intersphinx`` Sphinx extension.

.. _toml-technote-sphinx-intersphinx-projects:

[technote.sphinx.intersphinx.projects]
======================================

|optional|

A table of Sphinx project names and their root documentation URLs.

.. code-block:: toml

   [technote.sphinx.intersphinx.projects]
   python = "https://docs.python.org/3/"
   sphinx = "https://www.sphinx-doc.org/en/master/"

.. _toml-technote-sphinx-linkcheck:

[technote.sphinx.linkcheck]
===========================

|optional|

Configurations for the ``linkcheck`` Sphinx extension.

.. _toml-technote-sphinx-linkcheck-ignore:

ignore
------

|optional|

An array of regular expressions for URLs to ignore when checking links.
