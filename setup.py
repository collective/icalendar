import setuptools

version = '3.5'
shortdesc = 'iCalendar parser/generator'
longdesc = open('README.rst').read()
longdesc += open('CHANGES.rst').read()
longdesc += open('LICENSE.rst').read()
tests_require = ['unittest2']

setuptools.setup(
    name='icalendar',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
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
    install_requires=[
        'setuptools',
        'python-dateutil',
        'pytz',
    ],
    extras_require={
        'test': tests_require
    })
