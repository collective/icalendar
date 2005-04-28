#!/usr/bin/env python

from distutils.core import setup

f = open('version.txt', 'r')
version = f.read().strip()
f.close()

setup(name='icalendar',
      version=version,
      description='iCalendar support module',
      package_dir = {'': 'src'},
      packages=['icalendar'],
     )
