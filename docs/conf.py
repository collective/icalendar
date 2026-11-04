# icalendar documentation build configuration file
import datetime
import os
import sys
from pathlib import Path

import icalendar

HERE = Path(__file__).parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))  # update docs from icalendar source for livehtml

project = "icalendar"
this_year = datetime.date.today().year  # noqa: DTZ011
copyright = f"{this_year}, Plone Foundation"  # noqa: A001

extensions = [
    "notfound.extension",
    "sphinx.ext.apidoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",  # must be loaded after sphinx.ext.napoleon. See https://github.com/tox-dev/sphinx-autodoc-typehints/issues/15
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_icalendar",
    "sphinx_issues",
    "sphinx_llms_txt",
    "sphinx_reredirects",
]
source_suffix = {".rst": "restructuredtext"}
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

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
html_context = {
    "github_user": "collective",
    "github_repo": "icalendar",
    "github_version": "main",
    "doc_path": "docs",
}
# Custom fa-custom/fa-pypi icon used in icon_links above.
html_js_files = [
    ("js/custom-icons.js", {"defer": "defer"}),
]
html_static_path = ["_static"]
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/collective/icalendar",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
            "attributes": {"target": "_blank", "rel": "noopener me"},
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/icalendar",
            "icon": "fa-custom fa-pypi",
            "type": "fontawesome",
            "attributes": {"target": "_blank", "rel": "noopener me"},
        },
    ],
    "footer_start": ["nlnet", "donate"],
    "footer_center": "copyright",
    "footer_end": ["rtd-pr-previews", "theme-version", "sphinx-version"],
    "logo": {"text": "icalendar"},
    "navbar_start": ["navbar-logo", "version-switcher"],
    "navigation_with_keys": True,
    "search_bar_text": "Search",
    "secondary_sidebar_items": ["edit-this-page", "page-toc", "sourcelink"],
    "show_nav_level": 2,
    "show_toc_level": 2,
    "show_version_warning_banner": True,
    "switcher": {
        "json_url": json_url,
        "version_match": version_match,
    },
    "use_edit_page_button": True,
}
pygments_style = "sphinx"
smartquotes_action = "De"
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]


# -- linkcheck builder configuration ----------------------------------
# Ignore localhost
linkcheck_ignore = [
    # Ignore pages that require authentication
    r"https://app.readthedocs.org/dashboard/icalendar/users/create/",
    r"https://docutils.sourceforge.io/rst.html",
    r"https://github.com/collective/icalendar/fork",
    r"https://github.com/collective/icalendar/issues/new",
    r"https://github.com/collective/icalendar/settings/",
    r"https://groups.google.com/g/icalendar-coc/",
    r"https://pypi.org/manage/project/icalendar/collaboration/",
    # Ignore specific anchors
    r"https://github.com/actions/python-versions#support-policy",
    r"https://github.com/collective/icalendar/blob/7ca9db18c0847d1530520e01baf75f8ab8f4fa06/pyproject.toml#L32",
    r"https://github.com/collective/icalendar/blob/main/CODE_OF_CONDUCT.md#enforcement",
    r"https://github.com/collective/icalendar/blob/main/README.rst#related-projects",
    r"https://github.com/pre-commit/pre-commit-hooks#debug-statements",
    r"https://up-for-grabs.net/#/filters",
    # Ignore links that are unstable
    r"https://www.unicode.org/cldr/cldr-aux/charts/29/supplemental/zone_tzid.html",
]
linkcheck_anchors = True
linkcheck_timeout = 5
linkcheck_retries = 1


# -- nitpicky mode options ----------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-the-nitpicky-mode
# Use `make clean livehtml SPHINXOPTS="-n"`
nitpick_ignore_regex = [
    (
        r"py:.*",
        r"icalendar\.prop.*",
    ),  # Ignore old change log entry from before the re-org in 7.0.0a1
]


# -- notfound.extension configuration ----------------------------------
# https://sphinx-notfound-page.readthedocs.io/en/latest/configuration.html
notfound_template = "404.html"
# Defaults to READTHEDOCS_CANONICAL_URL's path on RTD. Outside RTD, that env
# var isn't set and the extension falls back to a hardcoded "/en/latest/",
# which 404s every asset on a local build. Use root-relative paths instead
# when not building on RTD.
if not os.environ.get("READTHEDOCS"):
    notfound_urls_prefix = "/"


# -- sphinx.ext.apidoc configuration -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/apidoc.html#
apidoc_modules = [
    {
        "path": "../src/icalendar",
        "destination": "reference/api",
        "exclude_patterns": [
            "**/tests*",
            "**/timezone/equivalent_timezone_ids_result*",
        ],
        "separate_modules": True,
        "automodule_options": {
            "ignore-module-all",
            "members",
            "show-inheritance",
            "undoc-members",
        },
    }
]


# -- sphinx.ext.autodoc configuration ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autoclass_content = "both"
autodoc_default_options = {
    "ignore-module-all": True,
    "no-inherited-members": "object,CaselessDict,str,bool,NamedTuple,int,float,Enum",
    "members": True,
    "show-inheritance": True,
    "undoc-members": True,
}


# -- sphinx.ext.intersphinx configuration ----------------------------------

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
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "typing": ("https://typing.python.org/en/latest/", None),
}


# -- sphinx.ext.napoleon configuration ----------------------------------
napoleon_use_param = True
napoleon_google_docstring = True
napoleon_attr_annotations = True


# -- sphinx_copybutton configuration ----------------------------------
# https://sphinx-copybutton.readthedocs.io/en/latest/use.html
# Exclude line numbers, prompts, and console output when copying code blocks.
copybutton_exclude = ".linenos, .gp, .go"


# -- sphinx_issues configuration ----------------------------------
# enables :issue:`N`, :pr:`N`, :user:`name` roles
issues_github_path = "collective/icalendar"

# -- sphinx_llms_txt builder configuration ----------------------------------
llms_txt_exclude = [
    "search",  # Exclude the search page
    "genindex",  # Exclude the index page
]


# -- sphinx_reredirects configuration ----------------------------------
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

# -- sphinxext.opengraph configuration -----------------------------------------
html_baseurl = os.environ.get(
    "READTHEDOCS_CANONICAL_URL", "https://icalendar.readthedocs.io/en/stable/"
)

ogp_site_url = html_baseurl
ogp_site_name = "icalendar"
ogp_description_length = 200
ogp_type = "website"
ogp_social_cards = {
    "image": "_static/img/pycal-icon.png",
    "image_mini": "_static/img/pycal-icon.png",
    "line_color": "#0f766e",
    "background_color": "#f8f7f4",
}


# -- man pages output ----------------------------------------------------------
man_pages = [("index", "icalendar", "icalendar Documentation", ["Plone Foundation"], 1)]


# -- HTML help output ----------------------------------------------------------
htmlhelp_basename = "icalendardoc"
