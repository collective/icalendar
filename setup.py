import os
import setuptools

version = '3.1'
shortdesc = 'iCalendar parser/generator'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__),
                              'docs', 'changelog.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()
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
    maintainer="Rok Garbas",
    maintainer_email="rok@garbas.si",
    author='MaxM',
    author_email='max@mxm.dk',
    url='https://github.com/collective/icalendar',
    license='BSD',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pytz',
    ],
    extras_require={
        'test': tests_require
    })
