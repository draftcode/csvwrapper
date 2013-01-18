#!/usr/bin/env python
# vim: fileencoding=utf-8
from setuptools import setup, find_packages

setup(
        name='csvwrapper',
        version='0.1.0',
        description='csv module with encoding conversion',
        author='draftcode',
        author_email='draftcode@gmail.com',
        url='https://github.com/draftcode/csvwrapper',
        packages=find_packages(),
        classifiers=[
                'Development Status :: 4 - Beta',
                'License :: OSI Approved :: MIT License',
                ],
        )

