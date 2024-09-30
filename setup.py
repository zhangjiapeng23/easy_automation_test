#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/21

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

PACKAGE = "easy_automation_test"

install_requires = [
    'allure-pytest>=2.12.0',
    'allure-python-commons>=2.12.0',
    'async-generator>=1.10',
    'async-timeout>=4.0.2',
    'atomicwrites>=1.4.0',
    'attrs>=21.2.0',
    'bleach>=3.3.1',
    'blinker>=1.7.0',
    'build>=0.5.1',
    'cachetools>=5.3.0',
    'certifi>=2021.5.30',
    'cffi>=1.15.0',
    'charset-normalizer>=2.0.3',
    'click>=8.1.7',
    'colorama>=0.4.4',
    'cryptography>=36.0.2',
    'docutils>=0.17.1',
    'exceptiongroup>=1.1.0',
    'Faker>=8.11.0',
    'flask>=3.0.2',
    'google-auth>=2.16.0',
    'gunicorn>=23.0.0',
    'h11>=0.13.0',
    'idna>=3.2',
    'importlib-metadata>=4.6.1',
    'iniconfig>=1.1.1',
    'itsdangerous>=2.1.2',
    'Jinja2>=3.1.3',
    'keyring>=23.0.1',
    'kubernetes>=25.3.0',
    'MarkupSafe>=2.1.5',
    'oauthlib>=3.2.2',
    'outcome>=1.1.0',
    'packaging>=21.0',
    'pep517>=0.11.0',
    'pkginfo>=1.7.1',
    'pluggy>=0.13.1',
    'py>=1.10.0',
    'pyasn1>=0.4.8',
    'pyasn1-modules>=0.2.8',
    'pycparser>=2.21',
    'Pygments>=2.9.0',
    'PyMySQL>=1.0.2',
    'pyOpenSSL>=22.0.0',
    'pyparsing>=2.4.7',
    'PySocks>=1.7.1',
    'pytest>=6.2.4',
    'python-dateutil>=2.8.2',
    'pywin32-ctypes>=0.2.0',
    'PyYAML>=5.3.1',
    'py-consul>=1.5.1',
    'readme-renderer>=29.0',
    'redis>=4.5.1',
    'requests>=2.26.0',
    'requests-oauthlib>=1.3.1',
    'requests-toolbelt>=0.9.1',
    'rfc3986>=1.5.0',
    'rsa>=4.9',
    'selenium>=4.8.0',
    'six>=1.16.0',
    'sniffio>=1.2.0',
    'sortedcontainers>=2.4.0',
    'text-unidecode>=1.3',
    'toml>=0.10.2',
    'tomli>=1.0.4',
    'tqdm>=4.61.2',
    'trio>=0.20.0',
    'trio-websocket>=0.9.2',
    'twine>=3.4.2',
    'urllib3>=1.26.6',
    'urllib3-secure-extra>=0.1.0',
    'waitress>=3.0.0',
    'webencodings>=0.5.1',
    'websocket-client>=1.5.1',
    'werkzeug>=3.0.1',
    'wsproto>=1.1.0',
    'zipp>=3.5.0',
    ]


def main():
    setuptools.setup(
        name=PACKAGE,
        version='0.0.8.6',
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