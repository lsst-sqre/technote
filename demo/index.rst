#############
Demo technote
#############

.. abstract::

   A *technote* is a web-native single page document that enables rapid technical communication within and across teams.

.. Three alphabets is a good guage for line length. We want to shoot for 2-3 alphabets.
.. abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz

Introduction
============

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. [#]_ Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

   This is a quote.

   It can span multiple paragraphs.

Quotes with attribution:

   This is a quote.

   It can span multiple paragraphs.

   -- The Developer

An epigraph:

.. epigraph::

   This is an epigraph.

   -- The Developer

.. [#] Footnote text. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

Method
======

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

A list:

- First item
- Second item
- Third item

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

.. code-block:: python
   :caption: hello.py

   print("Hello world")

Code cells
==========

This is a long code cell:

.. code-block:: Makefile
   :caption: Makefile

   .PHONY: update-deps
   update-deps:
   	pip install --upgrade pip-tools pip setuptools
   	pip-compile --upgrade --build-isolation --generate-hashes --output-file server/requirements/main.hashed.txt server/requirements/main.in
   	pip-compile --upgrade --build-isolation --generate-hashes --output-file server/requirements/dev.hashed.txt server/requirements/dev.in
   	pip-compile --upgrade --build-isolation --allow-unsafe --output-file server/requirements/main.txt server/requirements/main.in
   	pip-compile --upgrade --build-isolation --allow-unsafe --output-file server/requirements/dev.txt server/requirements/dev.in

   .PHONY: init
   init:
   	pip install --editable "./client[dev]"
   	pip install --editable ./server
   	pip install --upgrade -r server/requirements/main.txt -r server/requirements/dev.txt
   	rm -rf ./server.tox
   	pip install --upgrade pre-commit tox
   	pre-commit install

   .PHONY: update
   update: update-deps init

   .PHONY: run
   run:
   	cd server && tox run -e=run

Admonitions
===========

Some content.

.. attention::

   This is an attention notice.

More content.

.. caution::

   This is a caution:

   - First item
   - Second item
   - Third item

.. danger::

   This is a danger notice.

.. error::

   This is an error.

.. hint::

   This is a hint.

.. important::

   This is important.

.. note::

   This is a note.

.. tip::

   This is a tip.

.. warning::

   This is a warning.

Results
=======

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

Subsection
----------

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

Subsubsection
^^^^^^^^^^^^^

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

Second child subsubsection
^^^^^^^^^^^^^^^^^^^^^^^^^^

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

Third child subsubsection
^^^^^^^^^^^^^^^^^^^^^^^^^

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

Another subsection
------------------

Analysis
========

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.

Conclusion
==========

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin facilisis pharetra neque, at semper nulla mattis auctor. Proin semper mollis enim eget interdum. Mauris eleifend eget diam vitae bibendum. Praesent ut aliquet odio, sodales imperdiet nisi. Nam interdum imperdiet tortor sed fringilla. Maecenas efficitur mi sodales nulla commodo rutrum. Ut ornare diam quam, sed commodo turpis aliquam et. In nec enim consequat, suscipit tortor sit amet, luctus ante. Integer dictum augue diam, non pulvinar massa euismod in. Morbi viverra condimentum auctor. Nullam et metus mauris. Cras risus ex, porta sit amet nibh et, dapibus auctor leo.
