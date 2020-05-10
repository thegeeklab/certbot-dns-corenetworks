#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for the package."""

import io
import os
import re

from setuptools import find_packages
from setuptools import setup

PACKAGE_NAME = "certbot_dns_corenetworks"


def get_property(prop, project):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    result = re.search(
        r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop),
        open(os.path.join(current_dir, project, "__init__.py")).read(),
    )
    return result.group(1)


def get_readme(filename="README.md"):
    this = os.path.abspath(os.path.dirname(__file__))
    with io.open(os.path.join(this, filename), encoding="utf-8") as f:
        long_description = f.read()
    return long_description


setup(
    name=get_property("__project__", PACKAGE_NAME),
    description="Core Networks DNS Authenticator plugin for Certbot",
    keywords="dns, certbot, automation, corenetworks",
    version=get_property("__version__", PACKAGE_NAME),
    author=get_property("__author__", PACKAGE_NAME),
    author_email=get_property("__email__", PACKAGE_NAME),
    url=get_property("__url__", PACKAGE_NAME),
    license=get_property("__license__", PACKAGE_NAME),
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*.test", "test", "test.*"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,<4",
    entry_points={
        "certbot.plugins": [
            "dns-corenetworks = certbot_dns_corenetworks.dns_corenetworks:Authenticator"
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    install_requires=[
        "acme",
        "certbot>=0.15",
        "setuptools",
        "zope.interface",
        "corenetworks>=0.1.1",
    ],
    dependency_links=[],
)
