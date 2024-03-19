# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Roles Royce"
copyright = "2023, Karpatkey"
author = "Karpatkey"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.append(os.path.abspath("./_ext"))

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "autodoc_method",
    "sphinx_autodoc_typehints",
]

autoclass_content = "class"
# autodoc_typehints = "signature"
# autodoc_typehints_description_target = "documented_params"
# autodoc_typehints_format = "short"
# python_use_unqualified_type_names = True
autodoc_member_order = "bysource"
add_module_names = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
html_theme_options = {
    "description": "Execute transactions using Zodiac Roles Modifier contracts.",
    "page_width": "1200px",
    #'canonical_url': ,
    "extra_nav_links": {
        "Source code": "https://github.com/KarpatkeyDAO/roles_royce/",
        "Issue tracker": "https://github.com/KarpatkeyDAO/roles_royce/issues",
        "Karpatkey": "https://www.karpatkey.com/",
    },
}

autodoc_default_options = {
    "member-order": "bysource",
}
