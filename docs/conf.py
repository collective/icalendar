# icalendar documentation build configuration file
import datetime
import os
import sys
from pathlib import Path

import icalendar

HERE = Path(__file__).parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))  # update docs from icalendar source for livehtml

extensions = [
    "notfound.extension",
    "sphinx.ext.apidoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_reredirects",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",  # must be loaded after sphinx.ext.napoleon. See https://github.com/tox-dev/sphinx-autodoc-typehints/issues/15
]
source_suffix = {".rst": "restructuredtext"}
master_doc = "index"

project = "icalendar"
this_year = datetime.date.today().year  # noqa: DTZ011
copyright = f"{this_year}, Plone Foundation"  # noqa: A001

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Define the json_url for our version switcher.
json_url = "https://icalendar.readthedocs.io/en/latest/_static/version-switcher.json"

# Define the version we use for matching in the version switcher.
version_match = os.environ.get("READTHEDOCS_VERSION")
release = icalendar.__version__

# If READTHEDOCS_VERSION doesn't exist, we're not on RTD
# If it's an integer, we're in a PR build and the version isn't correct.
# If it's "latest", change to "dev" in the version switcher.
if not version_match or version_match.isdigit() or version_match == "latest":
    # For local development, infer the version to match from the package.
    if "a" in release or "b" in release or "rc" in release or "dev" in release:
        # Override the fully qualified URL in dev mode.
        json_url = "_static/version-switcher.json"
        version_match = "dev"
    else:
        version_match = f"v{release}"
elif version_match == "stable":
    version_match = f"v{release}"

exclude_patterns = [
    "reference/api/modules.rst",
]
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/collective/icalendar",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
            "attributes": {
                "target": "_blank",
                "rel": "noopener me",
                "class": "nav-link custom-fancy-css",
            },
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/icalendar",
            "icon": "fa-custom fa-pypi",
            "type": "fontawesome",
            "attributes": {
                "target": "_blank",
                "rel": "noopener me",
                "class": "nav-link custom-fancy-css",
            },
        },
    ],
    "logo": {"text": "icalendar"},
    "navbar_start": ["navbar-logo", "version-switcher"],
    "navigation_with_keys": True,
    "search_bar_text": "Search",
    "show_nav_level": 2,
    "show_toc_level": 2,
    "show_version_warning_banner": True,
    "switcher": {
        "json_url": json_url,
        "version_match": version_match,
    },
    "use_edit_page_button": True,
}
html_context = {
    #     "github_url": "https://github.com", # or your GitHub Enterprise site
    "github_user": "collective",
    "github_repo": "icalendar",
    "github_version": "main",
    "doc_path": "docs",
}
html_static_path = [
    "_static",
]
html_js_files = [
    ("js/custom-icons.js", {"defer": "defer"}),
]
napoleon_use_param = True
pygments_style = "sphinx"

# -- Intersphinx configuration ----------------------------------

# This extension can generate automatic links to the documentation of objects
# in other projects. Usage is simple: whenever Sphinx encounters a
# cross-reference that has no matching target in the current documentation set,
# it looks for targets in the documentation sets configured in
# intersphinx_mapping. A reference like :py:class:`zipfile.ZipFile` can then
# linkto the Python documentation for the ZipFile class, without you having to
# specify where it is located exactly.
#
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}


# -- linkcheck configuration ----------------------------------
# Ignore localhost
linkcheck_ignore = [
    # Ignore pages that require authentication
    r"https://app.readthedocs.org/dashboard/icalendar/users/create/",
    r"https://github.com/collective/icalendar/fork",
    r"https://github.com/collective/icalendar/settings/",
    r"https://groups.google.com/g/icalendar-coc/",
    r"https://pypi.org/manage/project/icalendar/collaboration/",
    # Ignore specific anchors
    r"https://github.com/collective/icalendar/blob/main/CODE_OF_CONDUCT.md#enforcement",
    r"https://github.com/collective/icalendar/blob/main/README.rst#related-projects",
    r"https://up-for-grabs.net/#/filters",
    # Ignore links that are unstable
    r"https://www.unicode.org/cldr/cldr-aux/charts/29/supplemental/zone_tzid.html",
]
linkcheck_anchors = True
linkcheck_timeout = 5
linkcheck_retries = 1

# -- Options for sphinx-notfound-page ----------------------------------
# https://sphinx-notfound-page.readthedocs.io/en/latest/configuration.html
notfound_template = "404.html"


# -- sphinx-reredirects configuration ----------------------------------
# https://documatt.com/sphinx-reredirects/usage.html
redirects = {
    "about": "index.html",
    "api": "reference/api/icalendar.html",
    "changelog": "reference/changelog.html",
    "cli": "how-to/cli.html",
    "credits": "contribute/credits.html",
    "contributing": "contribute/index.html",
    "install": "how-to/install.html",
    "license": "https://github.com/collective/icalendar/blob/main/LICENSE.rst",
    "maintenance": "contribute/maintenance.html",
    "security": "https://github.com/collective/icalendar/blob/main/SECURITY.md",
    "usage": "how-to/usage.html",
    }

man_pages = [("index", "icalendar", "icalendar Documentation", ["Plone Foundation"], 1)]

htmlhelp_basename = "icalendardoc"
