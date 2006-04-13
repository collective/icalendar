#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = file('version.txt').read().strip()

setup(name='icalendar',
      package_dir={'': 'src'},
      packages=['icalendar'],
      version=version,

      # metadata for upload to PyPI
      author='MaxM',
      author_email='maxm@mxm.dk',
      description='iCalendar parser/generator',
      license='GPL2.1',
      keywords='calendar icalendar',
      url='http://codespeak.net/icalendar/',
      long_description="""iCalendar is a parser/generator of iCalendar files 
          (RFC 2445) for use with Python.""",
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent'],
      platforms='All',
      )