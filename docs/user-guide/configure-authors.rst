####################################################
Specifying authors and contributors in technote.toml
####################################################

The :file:`technote.toml` file is where you specify the authors and other contributors to a technote.
This metadata is the basis for the author list in the technote's HTML and in :doc:`metadata exported <metadata>` from the technote HTML.
For a full reference of the schema for listing authors in :file:`technote.toml`, see :ref:`toml-technote-authors` and :ref:`toml-technote-contributors`.

Minimal author metadata
=======================

At a minimum, an author has a name.
Following metadata standards
The name needs to be structured into given (often the first) and family (often the last) name components.
This allows Technote to export your documents data to common formats like `CITATION.cff`_, Zenodo, and BibTeX.

.. code-block:: toml

   [[technote.authors]]
   name.given = "Vera C."
   name.family = "Rubin"

.. note::

   Note the dot syntax in the name; this is equivalent to the follow inline table TOML syntax:

   .. code-block:: toml

      [[technote.authors]]
      name = { "name": "Vera C. Rubin" }

``name`` is just one of many keys in a ``[[technote.authors]]`` table; documentation of how to add additional metadata are provided below.

Multiple authors
================

To add multiple authors, add extra ``[[technote.authors]]`` tables.
In TOML, the ``[[ ]]`` indicates an **array** of tables.

.. code-block:: toml

   [[technote.authors]]
   name.given = "Arno A."
   name.family = "Penzias"

   [[technote.authors]]
   name.given = "Robert W."
   name.family = "Wilson"

Each author can have rich metadata, as described next.

Additional author metadata
==========================

Besides the ``name`` key, authors can have additional metadata (see the :ref:`[[technote.authors]] <toml-technote-authors>` reference).
The author's email, ORCiD identifier, an internal identifier, and affiliations can be added.

.. code-block:: toml

   [[technote.authors]]
   name.given = "Jonathan"
   name.family = "Sick"
   email = "jsick@lsst.org"
   orcid = "https://orcid.org/0000-0003-3001-676X"
   internal_id = "sickj"

Note that any of these additional fields can be omitted if the metadata isn't available or appropriate.

The ``orcid`` field, if set, must be a full URL, not just the path component of the ORCiD.

The ``internal_id`` is meant to have meaning within the specific organization authoring technotes.
For example, Rubin Observatory keeps a database of authors.
Including the ``internal_id`` enables Rubin to automatically update and augment metadata in individual technotes based on that author database.

Adding affiliations
===================

A ``[[technote.authors]]`` table can include an array of affiliations tables.
These tables can be inline, if brief:

.. code-block:: toml

   [[technote.authors]]
   name.given = "Jonathan"
   name.family = "Sick"
   orcid = "https://orcid.org/0000-0003-3001-676X"
   affiliations = [
       { name = "J.Sick Codes" }
       { name = "Rubin Observatory", ror = "https://ror.org/048g3cy84" }
   ]

Or as full ``[[technote.authors.affiliations]]`` tables:

.. code-block:: toml

   [[technote.authors]]
   name.given = "Jonathan"
   name.family = "Sick"
   orcid = "https://orcid.org/0000-0003-3001-676X"

   [[technote.authors.affiliations]]
   name = "J.Sick Codes"

   [[technote.authors.affiliations]]
   name = "Rubin Observatory", ror = "https://ror.org/048g3cy84" }
   ]

Non-author contributors
=======================

People other than authors might contribute to a technote.
For example, a contact, an editor, or a project manager.
Each non-author contributor can be marked up with a specific role.

To start, each contributor is a ``[[technote.contributors]]`` table.
Contributors take the same keys as authors (``[[technote.authors]]``), but with additional ``role`` and ``note`` fields.

The ``role`` can be any string from the Zenodo vocabulary for roles (`technote.metadata.zenodo.ZenodoRole`).

.. code-block:: toml

   [[technote.contributors]]
   name.given = "Frossie"
   name.family = "Economou"
   role = "ProjectManager"

For the ``Other`` role, you can clarify it with a free-form text statement in the ``note`` key.
