import os
import setuptools

version = '3.0.1b1'

setuptools.setup(
    name='icalendar',
    version=version,
    description="iCalendar parser/generator",
    long_description=open("README.rst").read() + \
            open(os.path.join('docs', 'changelog.rst')).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        ],
    keywords='calendar calendaring ical icalendar event todo journal '
             'recurring',
    maintainer="Rok Garbas",
    maintainer_email="rok@garbas.si",
    author='MaxM',
    author_email='max@mxm.dk',
    url='https://github.com/collective/icalendar',
    license='GPL',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    extras_require={
        'test': ['unittest2'],
        },
    )
