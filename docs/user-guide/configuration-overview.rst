##################################
Overview of technote configuration
##################################

Technote builds technote documents using Sphinx_.
Virtually anything you can accomplish in a general Sphinx project your can also include in a technote.
To simplify the set up process, Technote provides its own configuration system that layers on top of Sphinx's.
This page explains that configuration system.

The technote.toml and conf.py files
===================================

Besides the content file, technotes have at least two other files: :file:`technote.toml` and :file:`conf.py`.

:file:`technote.toml` is unique to Technote, and is what you'll work with most often.
This file is where you can both mark up bibliographic metadata about your technote and also configure the Sphinx_ build.
A basic :file:`technote.toml` file might look like this:

.. literalinclude:: ../../demo/rst/technote.toml
   :caption: conf.py

To learn about all the available keys in :file:`technote.toml`, see :doc:`technote-toml`.
This user guide also includes a number of :ref:`how-to guides on specific aspects of the configuration <toc-config>`.

The other configuration file is :file:`conf.py` — the standard Sphinx configuration file.
At a minimum, the Sphinx configuration imports the base technote configuration:

.. code-block:: python
   :caption: conf.py

   from technote.sphinxconf import *

If you are using a theme for an organization, you will import *its* configuration module instead.
For example, Rubin technote use a configuration from `Documenteer <https://documenteer.lsst.io>`_:

.. code-block:: python
   :caption: conf.py

   from documenteer.conf.technote import *

Primer on TOML
==============

:file:`technote.toml` is written in TOML_ syntax.
If you've written YAML before, you'll be fairly comfortable, but TOML does have a number of distinct features.
The first unique feature to note is that mappings or objects (key-value pairs) are described with *tables* and those tables are preceded by their key in square brackets.

.. code-block:: toml

   [technote]  # the technote table
   id = "SQR-000"  # a key in the table, aka technote.id

Tables can be nested.
For example, the ``sphinx`` table inside the ``technote`` table:

.. code-block:: toml

   [technote.sphinx]
   extensions = ["sphinx_diagrams"]

TOML supports resolving keys in tables using dots (``.``) to separate each level of hierarchy.
So the same TOML configuration as above can be expressed as:

.. code-block:: toml

   [technote]
   sphinx.extensions = ["sphinx_diagrams"]

The :file:`technote.toml` configuration frequently uses *arrays of tables*, such as when listing authors.
Arrays of tables are the key name, in double brackets.
You can repeat the tables for each item:

.. code-block:: toml

   [[technote.authors]]
   name.given = "Jonathan"
   name.family = "Sick"

   [[technote.authors]]
   name.given = "Frossie"
   name.family = "Economou"

To learn all about the TOML syntax, see the `TOML specification website`__.

How the configuration system works with the Sphinx build
========================================================

If your are curious how the Sphinx build uses :file:`technote.toml`,

When a Sphinx build starts (by running ``sphinx-build``), it automatically reads the project's configuration file (:file:`conf.py`).
In technote projects, the :file:`conf.py` file always imports the base technote configuration module, either directly or through a theme's configuration file (``from technote.sphinxconf import *``).
The Technote configuration module, in turn, loads :file:`technote.toml` and then sets Sphinx configuration variables based on that input.
