#################
Release procedure
#################

This page gives an overview of how technote releases are made.
This information is only useful for maintainers.

technote's releases are largely automated through GitHub Actions (see the `ci.yaml`_ workflow file for details).
When a semantic version tag is pushed to GitHub, `technote is released to PyPI`_ with that version.
Similarly, documentation is built and pushed for each version (see https://technote.lsst.io/v).

.. _`technote is released to PyPI`: https://pypi.org/project/technote/
.. _`ci.yaml`: https://github.com/lsst-sqre/technote/blob/main/.github/workflows/ci.yaml

.. _regular-release:

Regular releases
================

Regular releases happen from the ``main`` branch after changes have been merged.
From the ``main`` branch you can release a new major version (``X.0.0``), a new minor version of the current major version (``X.Y.0``), or a new patch of the current major-minor version (``X.Y.Z``).
See :ref:`backport-release` to patch an earlier major-minor version.

Release tags are semantic version identifiers following the :pep:`440` specification.

1. Change log and documentation
-------------------------------

Each PR should include updates to the change log.
If the change log or documentation needs additional updates, now is the time to make those changes through the regular branch-and-PR development method against the ``main`` branch.

In particular, replace the "Unreleased" section headline with the semantic version and date.
See :ref:`dev-change-log` in the *Developer guide* for details.

2. GitHub release and tag
-------------------------

Use `GitHub's Release feature <https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository>`__ to create releases and their corresponding Git tags.

1. Specify a tag from the appropriate branch (typically ``main``).
   This tag's name is :pep:`440` and is usually formatted at ``X.Y.Z`` (without a ``v`` prefix).

2. For the release name, repeat the version string.

3. Fill in the release notes, copied from the release notes.
   You can use GitHub's change log feature to additionally generate a list of PRs included in the release.

The tag **must** follow the :pep:`440` specification since technote uses setuptools_scm_ to set version metadata based on Git tags.
In particular, **don't** prefix the tag with ``v``.

.. _setuptools_scm: https://github.com/pypa/setuptools_scm

The `ci.yaml`_ GitHub Actions workflow uploads the new release to PyPI and documentation to https://technote.lsst.io.

.. _backport-release:

Backport releases
=================

The regular release procedure works from the main line of development on the ``main`` Git branch.
To create a release that patches an earlier major or minor version, you need to release from a **release branch.**

Creating a release branch
-------------------------

Release branches are named after the major and minor components of the version string: ``X.Y``.
If the release branch doesn't already exist, check out the latest patch for that major-minor version:

.. code-block:: sh

   git checkout X.Y.Z
   git checkout -b X.Y
   git push -u

Developing on a release branch
------------------------------

Once a release branch exists, it becomes the "main" branch for patches of that major-minor version.
Pull requests should be based on, and merged into, the release branch.

If the development on the release branch is a backport of commits on the ``main`` branch, use ``git cherry-pick`` to copy those commits into a new pull request against the release branch.

Releasing from a release branch
-------------------------------

Releases from a release branch are equivalent to :ref:`regular releases <regular-release>`, except that the release branch takes the role of the ``main`` branch.
