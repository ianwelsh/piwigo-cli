#!/usr/bin/env python
'''
Installer script for ripper.
'''

from setuptools import setup

setup (
    name = "ripper",
    description = "Automatically transcode and upload FLACs on What.CD.",
    author = 'Zach Denton',
    author_email = 'zacharydenton@gmail.com',
    version = '1.0',
    url = 'http://zacharydenton.com/code/whatbetter/',
    py_modules = ['ripper'],
    scripts = ['ripper'],
    install_requires = [
                'argparse',
                'BeautifulSoup',
                ]
)
