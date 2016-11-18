# -*- coding: utf-8 -*-
import codecs
import setuptools
import sys
import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/icalendar/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


shortdesc = 'iCalendar parser/generator'
longdesc = codecs.open('README.rst', encoding='utf-8').read()
longdesc += codecs.open('CHANGES.rst', encoding='utf-8').read()
longdesc += codecs.open('LICENSE.rst', encoding='utf-8').read()


tests_require = []
install_requires = [
    'python-dateutil',
    'pytz',
    'setuptools',
]

if sys.version_info[:2] == (2, 6):
    # Python unittest2 only needed for Python 2.6
    tests_require.append('unittest2')
    # OrderedDict was added in 2.7
    install_requires.append('ordereddict')


setuptools.setup(
    name='icalendar',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    keywords='calendar calendaring ical icalendar event todo journal '
             'recurring',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/collective/icalendar',
    license='BSD',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': tests_require
    },
    test_suite='icalendar.tests'
)
