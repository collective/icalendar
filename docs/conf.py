# -*- coding: utf-8 -*-
# icalendar documentation build configuration file
import ast
import datetime
import os
import re
import sys

base_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
_version_re = re.compile(r'__version__\s+=\s+(.*)')

sys.path.append(os.path.join(base_dir, 'src'))

try:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
except ImportError:
    html_theme = 'default'
    if not on_rtd:
        print('-' * 74)
        print('Warning: sphinx-rtd-theme not installed, building with default '
              'theme.')
        print('-' * 74)

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode'
]
source_suffix = '.rst'
master_doc = 'index'

project = u'icalendar'
this_year = datetime.date.today().year
copyright = u'{}, Plone Foundation'.format(this_year)

# Read the version number
with open(os.path.join(base_dir, 'src/icalendar/__init__.py')) as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

release = version

exclude_patterns = ['_build', 'lib', 'bin', 'include', 'local']
pygments_style = 'sphinx'

htmlhelp_basename = 'icalendardoc'

man_pages = [
    ('index', 'icalendar', u'icalendar Documentation',
     [u'Plone Foundation'], 1)
]
