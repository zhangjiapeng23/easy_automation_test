#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/20
import importlib


class SettingLoader:

    def __init__(self, settings_filename):
        settings_package = 'settings'
        settings_filename = f".{settings_filename}"
        _settings = importlib.import_module(settings_filename, package=settings_package)
        for setting in dir(_settings):
            if setting.isupper():
                value = getattr(_settings, setting)
                setattr(self, setting, value)

    def merge_from(self, other_settings):
        if not (isinstance(other_settings, SettingLoader)):
            raise RuntimeError("merge object must be an instance of Setting")

        for other_setting in dir(other_settings):
            if other_setting.isupper() and other_setting not in dir(self):
                value = getattr(other_settings, other_setting)
                setattr(self, other_setting, value)

    def merge_to(self, other_settings):
        if not (isinstance(other_settings, SettingLoader)):
            raise RuntimeError("merge object must be an instance of Setting")

        for other_setting in dir(other_settings):
            if other_setting.isupper():
                value = getattr(other_settings, other_setting)
                setattr(self, other_setting, value)



