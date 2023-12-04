####################################
Theming an organizations's technotes
####################################

Technotes are intended to be branded and customized by each organization that creates and publishes theme.
The general steps for creating a technote theme are:

1. Create a Python package that individual technote projects can import (such as from PyPI, conda-forge, or even GitHub). This package needs to include ``technote`` as a dependency. For example, Rubin Observatory uses Documenteer_ (https://github.com/lsst-sqre/documenteer) as its theme package.

2. Create a configuration module that imports the base technote configuration and then appends any additional Sphinx configurations.

   .. code-block:: python

      from technote.sphinxconf import *

      # Add additional configurations below

   For an example, see `Documenteer's configuration module <https://documenteer.lsst.io/technotes/configuration.html#configuration-source-reference>`__.

   To access metadata and configuration from :file:`technote.toml`, use the ``T`` variable exported from ``technote.sphinxconf``, which is an instance of `~technote.main.TechnoteSphinxConfig`.

3. Add custom CSS. Declare the CSS file in your package to the ``html_static_path`` variable in the Sphinx configuration module, and then append the name of that CSS file to the ``html_css_files`` list in the Sphinx configuration module.

4. Add Jinja custom templates that override the built-in ones from technote (`see the templates on GitHub <https://github.com/lsst-sqre/technote/tree/main/src/technote/theme>`__). Declare the directory in your package containing these templates to the ``templates_path`` variable in the Sphinx configuration module.

5. Set the logos and the logos' links by setting ``html_theme_options``. For example:

   .. code-block:: python

      html_theme_options = {
          "light_logo": "rubin-imagotype-color-on-white-crop.svg",
          "dark_logo": "rubin-imagotype-color-on-black-crop.svg",
          "logo_link_url": "https://www.lsst.io",
          "logo_alt_text": "Rubin Observatory logo",
      }

   Don't forget to declare the path locations of image assets in your package to the ``html_static_path`` variable in the Sphinx configuration module.
