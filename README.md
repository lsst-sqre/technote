# Technote

Rubin Observatory's framework for Sphinx-based technote documents.
Learn more at https://technote.lsst.io.

Install from PyPI:

```sh
pip install technote
```

technote is developed by Rubin Observatory at https://github.com/lsst-sqre/technote.

## Features

> **Warning**
> Technote is in initial design and development.
> The features described below may not be implemented yet.

*Technotes* are web-native, single page websites that facilitate rapid scientific and technical communication.
The "technote" package provides the framework for creating technotes:

- A Sphinx theme optimized for single page documents, like technotes.
  This theme can be customized by organizations.
- A `technote.toml` makes it easy to configure document metadata.
- Technotes can be written in reStructuredText, Markdown, or as Jupyter notebooks.

## Developing technote

The best way to start contributing to technote is by cloning this repository, creating a virtual environment, and running the `make init` command to set up the Python project:

```sh
git clone https://github.com/lsst-sqre/technote.git
cd technote
make init
```

Technote also uses [Webpack](https://webpack.js.org/) to bundle CSS and JS.
We use [nvm](https://github.com/nvm-sh/nvm) to set up Node at a specific version:

```sh
nvm use
```

This may happen automatically when opening the technote repo in your shell.

Then install the JS dependencies:

```sh
npm install
```

And build the CSS and JS assets:

```sh
npm run build
```

You can run tests and build documentation with [tox](https://tox.wiki/en/latest/):

```sh
tox
```

To learn more about the individual environments:

```sh
tox -av
```

In particular, to build a demo technote in the [demo](./demo) directory:

```sh
tox -e demo
```

[See the docs for more information.](https://technote.lsst.io/dev/development.html)
