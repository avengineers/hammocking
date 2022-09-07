# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'HammocKing'
copyright = '2022, RMT guys'
author = 'RMT guys'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinxcontrib.plantuml',
    'sphinx.ext.githubpages'
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
#html_static_path = ['_static']

html_theme_options = {
    'navigation_depth': 4,
}

html_baseurl = 'https://avengineers.github.io/hammocking'


# -- Options for Image generation with plantuml ------------------------------
# https://github.com/sphinx-contrib/plantuml#configuration

plantuml_output_format = 'svg'

import os
if os.name == 'nt':
    plantuml = 'plantuml.cmd'
