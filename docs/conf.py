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
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
source_suffix = {".rst": "restructuredtext"}
master_doc = "index"

project = "icalendar"
this_year = datetime.date.today().year  # noqa: DTZ011
copyright = f"{this_year}, Plone Foundation"  # noqa: A001

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

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
                "class": "nav-link custom-fancy-css"
            }
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/icalendar",
            "icon": "fa-custom fa-pypi",
            "type": "fontawesome",
            "attributes": {
                "target": "_blank",
                "rel": "noopener me",
                "class": "nav-link custom-fancy-css"
            }
        },
    ],
    "logo": {
        "text": "icalendar"
    },
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
pygments_style = "sphinx"

man_pages = [("index", "icalendar", "icalendar Documentation", ["Plone Foundation"], 1)]

htmlhelp_basename = "icalendardoc"
