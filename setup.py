from setuptools import setup

from geoadmin.version import __version__ as version


with open("README.rst", "r") as fp:
    description = fp.read() + "\n"

setup(
    name="django-geoadmin",
    version=version,
    description="Django Geo Admin",
    long_description=description,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Development Status :: 4 - Beta',
        "Framework :: Django",
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    ],
    keywords="django admin leaflet map list view",
    license='LGPL',
    packages=['geoadmin'],
    package_data={
        'geoadmin': [
            'templates/geoadmin/geoadmin_change_list.html',
            'templates/geoadmin/geoadmin_view.html',
            'static/geoadmin/geoadmin.css',
            'static/geoadmin/geoadmin.js',
        ]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "django",
        "django-leaflet",
    ],
)
