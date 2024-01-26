#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/21

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

PACKAGE = "easy_automation_test"

install_requires=[
        'requests>=2.26.0',
        'selenium>=4.8.0',
        'allure-pytest>=2.12.0',
        'PyYAML>=5.4.1',
        'Faker>=8.10.1',
        'pytest-xdist>=2.3.0',
        'kubernetes>=25.3.0',
        'tornado>=6.2',
        'redis>=4.5.1',
        'pytest>=6.2.4',
        'PyMySQL>=1.0.2'
    ]


def main():
    setuptools.setup(
        name=PACKAGE,
        version='0.0.7.0',
        author='jameszhang',
        author_email='18373230129@163.com',
        description='Easy to create a web or api automation test project',
        long_description=long_description,
        long_description_content_type='text/markdown',
        keywords=['automation test', 'web', 'api'],
        url="https://github.com/zhangjiapeng23/easy_automation_test",
        project_urls={
            "Bug Tracker": "https://github.com/zhangjiapeng23/easy_automation_test/issues"
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        install_requires=install_requires,
        packages=setuptools.find_packages(where="src"),
        package_dir={"": "src"},
        py_modules=['easy_test'],
        include_package_data=True,
        python_requires=">=3.9",
        entry_points={
            'console_scripts': [
                'easy-automation=easy_automation.utils.command_parser:command_parser'
            ],
            "pytest11":
                ["easy_automation_pytest=easy_automation.core.plugin"]

        }
    )


if __name__ == '__main__':
    main()