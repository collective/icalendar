import codecs
import setuptools
import sys
import os.path
from re import search, M

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

version = str(find_version('src/icalendar', '__init__.py'))
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
    }
)
