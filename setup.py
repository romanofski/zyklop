# coding: utf-8
from setuptools import setup, find_packages
from zyklop import __author__
from zyklop import __author_email__
from zyklop import __description__
from zyklop import __name__
from zyklop import __version__


setup(
    name=__name__,
    version=__version__,
    description=__description__,
    long_description=(
        open("README.rst").read() + '\n\n' +
        open("docs/CHANGES.txt").read()
    ),
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Archiving :: Mirroring",
        "Topic :: System :: Systems Administration",
    ],
    keywords='server',
    author=__author__,
    author_email=__author_email__,
    url='http://zyklop.rtfd.org',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'paramiko',
        'argparse',
    ],
    extras_require=dict(
        test=['mock', ]
    ),
    entry_points={
        'console_scripts': [
            'zyklop = zyklop.command:sync',
        ]
    }
)
