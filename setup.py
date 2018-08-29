#!/usr/bin/env python
"""
Installer script for ripper.
"""

from setuptools import setup

setup(
    name="piwigo",
    description="CLI and SDK for Piwigo",
    author="Alex Phillips",
    author_email="ahp118@gmail.com",
    version="1.0",
    url="",
    py_modules=["piwigo"],
    entry_points = {
        'console_scripts': [
            'piwigo = piwigo.cli:main'
        ]
    },
    install_requires=["requests"],
)
