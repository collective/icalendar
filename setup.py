from setuptools import setup
from setuptools import find_packages

version = '2.2'

setup(
    name='icalendar',
    version=version,
    description="iCalendar parser/generator",
    long_description=open("README.rst").read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        ],
    keywords='calendar calendaring ical icalendar event todo journal recurring',
    author='MaxM',
    author_email='max@mxm.dk',
    url='https://gihub.com/collective/iCalendar',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        ],
    extras_require={
        'test': [
            'unittest2',
            ],
        },
    )
