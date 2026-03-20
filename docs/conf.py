# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
from pathlib import Path

from sphinx_needs import __version__ as sphinx_needs_version

print ('sphinx-needs version: ' + str(sphinx_needs_version))

sources_path = Path(__file__).parent.parent.joinpath("src")
sys.path.insert(0, sources_path.as_posix())


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Hammocking"
copyright = "2025, RMT"
author = "RMT"
release = "0.9.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

# https://myst-parser.readthedocs.io/en/latest/intro.html
extensions.append("myst_parser")

# TODO: enable this extension when is is supported by readthedocs
# draw.io config - @see https://pypi.org/project/sphinxcontrib-drawio/
# extensions.append("sphinxcontrib.drawio")
# drawio_default_transparency = True

# mermaid config - @see https://pypi.org/project/sphinxcontrib-mermaid/
extensions.append("sphinxcontrib.mermaid")

# Configure extensions for include doc-strings from code
extensions.extend(
    [
        "sphinx.ext.autodoc",
        "sphinx.ext.autosummary",
        "sphinx.ext.napoleon",
        "sphinx.ext.viewcode",
        "sphinx_new_tab_link",
    ]
)

# Resize rtd theme
extensions.append("sphinx_rtd_size")
sphinx_rtd_size_width = "90%"

# sphinx_needs
extensions.append("sphinx_needs")

needs_from_toml = "ubproject.toml"

# copy button for code block
extensions.append("sphinx_copybutton")

# The suffix of source filenames.
source_suffix = [
    ".rst",
    ".md",
]

templates_path = ["_templates"]
exclude_patterns = ["build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# html_static_path = ["_static"]
