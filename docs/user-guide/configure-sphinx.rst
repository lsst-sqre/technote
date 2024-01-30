############################
Configuring the Sphinx build
############################

Technote builds upon Sphinx_.
This means that any Sphinx syntax and extensions are available to technotes.
Although Technote has its own default configurations for the Sphinx build, you can customize some common Sphinx configurations in the :file:`technote.toml` file, or by directly editing the :file:`conf.py` file.

Adding Sphinx extensions
========================

The most common configuration is to add additional Sphinx extensions.
You can do this with the ``extensions`` key in the ``[technote.sphinx]`` table:

.. code-block:: toml
   :caption: technote.toml

   [technote.sphinx]
   extensions = ["sphinx_diagrams"]

Note that these extensions are *in addition* to the default extensions provided by Technote and any custom theme.

Once added through the ``extensions`` array in :file:`technote.toml`, you can add configurations for that extension in the Sphinx :file:`conf.py` file.
See :ref:`direct-sphinx-conf`.

.. important::

   Remember to also install the extension, as necessary.
   This might be done by adding the extension's package to your :file:`requirements.txt` file, or similar.

Link to other documentation with intersphinx
============================================

Intersphinx_ is a built-in Sphinx extension that helps you link to other sphinx projects (including other technotes and many Python project documentation sites including `docs.astropy.org <https://docs.astropy.org/en/stable/>`__ and `docs.python.org <https://docs.python.org/3/>`__.)

To add a site to the Intersphinx_ configuration, add items to the ``[technote.sphinx.intersphinx]`` table:

.. code-block:: toml
   :caption: technote.toml

   [technote.sphinx.intersphinx.projects]
   astropy = "https://docs.astropy.org/en/stable/"
   python = "https://docs.python.org/3/"

Keys are the names of projects, and also become prefixes for ``ref`` directives to that project.

For information on using Intersphinx_ to make cross-project links, see the `Sphinx documentation <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html>`__.

Configuring the "nitpick" settings
==================================

Sphinx's "nitpick" mode elevates build warnings into errors.
You might want to enable this mode if you want catch any issues in your documents build.
Technote doesn't enable nitpick mode by default because it can be challenging to understand some types of Sphinx warnings.

To enable nitpick mode:

.. code-block:: toml
   :caption: technote.toml

   [technote.sphinx]
   nitpick = true

If some types of errors are unavoidable, you can configure Sphinx to ignore them.
Errors in Sphinx have types (e.g. the ``py:obj`` role) and targets (the argument of the role).
For example, to ignore all errors related to FastAPI API links:

.. code-block:: toml
   :caption: technote.toml

   [technote.sphinx]
   nitpick = true
   nitpick_ignore_regex = [
     ['py:obj', 'fastapi\.*']
   ]

This regex syntax allows you to match multiple types and targets.
Use TOML's literal string syntax (single quotes, rather than double quotes) to avoid escaping backslashes.
An alternative key, ``nitpick_ignore``, is available is you don't need to use regular expression syntax.

See the `Sphinx nitpick configuration documentation <https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-nitpick_ignore>`__ for more details.

Configuring the linkcheck builder
=================================

Sphinx's linkcheck builder allows you to verify that links in your technote are resolvable on the internet.
Some links may be inherently unresolvable (because of auth), or be known to be intermittently unavailable.
You can ignore such links with the ``[technote.sphinx.linkcheck]`` table's ``ignore`` array.

.. code-block:: toml
   :caption: technote.toml

   [technote.sphinx.linkcheck]
   ignore = [
     'https://docushare\.lsstcorp\.org/.*'
   ]

Items in the ``ignore`` array are interpreted as Python regular expressions.
Therefore, use single quotes for a literal TOML string to avoid escaping backslashes.

For more information, see `the Sphinx linkcheck configuration documentation <https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-the-linkcheck-builder>`__.

.. _direct-sphinx-conf:

Directly configuring Sphinx and extensions
==========================================

Sphinx and its extensions take configurations beyond those accessible from the :file:`technote.toml` file.
You can still make those configurations in the :file:`conf.py` file.

.. code-block:: python
   :caption: conf.py

   from technote.sphinxconf import *  # noqa: F403

   primary_domain = "math"

Generally add your configurations *after* the base technote configuration is imported (i.e., after ``from technote.sphinxconf import *``, or your theme's equivalent) to override any default configurations.

For more information about Sphinx configurations, see the `Sphinx documentation <https://www.sphinx-doc.org/en/master/usage/configuration.html>`__ or the documentation for an extension.
