# coding: utf-8
from setuptools import setup, find_packages

version = '0.4'

setup(
    name='zyklop',
    version=version,
    description="Rsync wrapper making syncing easy",
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
    author='Róman Joost',
    author_email='roman@bromeco.de',
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
            'zyklop = zyklop:sync',
        ]
    }
)
