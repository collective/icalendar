# icalendar documentation build configuration file
import importlib.metadata
import datetime
import os

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

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
    'sphinx.ext.viewcode',
    'sphinx_copybutton'
]
source_suffix = '.rst'
master_doc = 'index'

project = 'icalendar'
this_year = datetime.date.today().year
copyright = f'{this_year}, Plone Foundation'
version = importlib.metadata.version('icalendar')
release = version

exclude_patterns = ['_build', 'lib', 'bin', 'include', 'local']
pygments_style = 'sphinx'

htmlhelp_basename = 'icalendardoc'

man_pages = [
    ('index', 'icalendar', 'icalendar Documentation',
     ['Plone Foundation'], 1)
]
