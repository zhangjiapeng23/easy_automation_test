#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/21

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='easy-automation-test',
    version='0.0.0',
    author='jameszhang',
    author_email='18373230129@163.com',
    description='Easy to create a web, mobile or api automation test project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/zhangjiapeng23/easy_automation_test",
    project_urls={
        "Bug Tracker": "https://github.com/zhangjiapeng23/easy_automation_test/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'easy-automation=easy_automation.utils.command_parser:command_parser'
        ]
    }
)