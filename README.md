# technote

Rubin Observatory's framework for Sphinx-based technote documents.
Learn more at https://technote.lsst.io

Install from PyPI:

```sh
pip install technote
```

technote is developed by Rubin Observatory at https://github.com/lsst-sqre/technote.

## Features

<!-- A bullet list with things that this package does -->

## Developing technote

The best way to start contributing to technote is by cloning this repository, creating a virtual environment, and running the `make init` command:

```sh
git clone https://github.com/lsst-sqre/technote.git
cd technote
make init
```

You can run tests and build documentation with [tox](https://tox.wiki/en/latest/):

```sh
tox
```

To learn more about the individual environments:

```sh
tox -av
```

[See the docs for more information.](https://technote.lsst.io/dev/development.html)
