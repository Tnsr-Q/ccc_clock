# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'CCC Clock'
copyright = '2024, CCC Clock Team'
author = 'CCC Clock Team'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

source_suffix = '.rst'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']