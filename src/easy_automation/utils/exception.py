#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/19


class BrowserNotSupport(Exception):

    def __init__(self, name):
        self.browser_name = name
        self.msg = '{} browser is not supported.'

    def __str__(self):
        return self.msg.format(self.browser_name)


class SeleniumHubNotSet(Exception):

    def __str__(self):
        return 'if run in prod module, should set selenium hub server url in settings'


class SeleniumHubUrlInvalid(Exception):

    def __init__(self, selenium_url):
        self.url = selenium_url

    def __str__(self):
        return 'selenium url: {} in settings is invalid.'


class ProjectHostNotSet(Exception):

    def __str__(self):
        return 'Project host not set in settings.'


class CommandError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PathFindError(Exception):

    def __str__(self):
        return "Can't find manage.py file, please make sure this file " \
               "under project root dir"
