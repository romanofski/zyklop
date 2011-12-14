from setuptools import setup, find_packages

version = '0.1'

setup(
    name='zyklop',
    version=version,
    description="Administrate servers",
    long_description="",
    classifiers=[
        "Programming Language :: Python 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='server',
    author='Roman Joost',
    author_email='roman@bromeco.de',
    url='',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'fabric',
    ],
    extras_require=dict(
        test=['mocker',]
    ),
    entry_points = {
        'console_scripts': [
            'sync = zyklop.sync:sync',
        ]
    }
)
