from setuptools import setup, find_packages

version = '0.1'

setup(
    name='zyklop',
    version=version,
    description="Find to sync large files",
    long_description="",
    classifiers=[
        "Programming Language :: Python 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='server',
    author='Roman Joost',
    author_email='roman@bromeco.de',
    url='http://zyklop.rtfd.org',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'paramiko',
    ],
    extras_require=dict(
        test=['mocker', ]
    ),
    entry_points={
        'console_scripts': [
            'zyklop = zyklop:sync',
        ]
    }
)
