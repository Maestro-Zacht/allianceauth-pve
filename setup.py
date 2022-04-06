#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = []

test_requirements = []

setup(
    author="Matteo Ghia",
    author_email='matteo.ghia@yahoo.it',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    description="PvE tool for AllianceAuth",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='allianceauth_pve',
    name='allianceauth_pve',
    packages=find_packages(include=['allianceauth_pve', 'allianceauth_pve.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Maestro-Zacht/allianceauth-pve',
    version='0.1.0',
    zip_safe=False,
)
