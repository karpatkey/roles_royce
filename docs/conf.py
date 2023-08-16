# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Roles Royce'
copyright = '2023, Karpatkey'
author = 'Karpatkey'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
]

#autodoc_typehints = "signature"
#autodoc_typehints_description_target = "documented_params"
#autodoc_typehints_format = "short"
#python_use_unqualified_type_names = True
autodoc_member_order = 'bysource'
add_module_names = False

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_theme_options = {
    'page_width': '1200px',
}

autodoc_default_options = {
    'member-order': 'bysource',
}

def maybe_skip_member(app, what, name, obj, skip, options):
    print(app, what, name, obj, skip, options)
    if name in ["fixed_arguments", "target_address"]:
        return False

def setup(app):
    app.connect('autodoc-skip-member', maybe_skip_member)
