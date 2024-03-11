#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/20
import importlib
import sys

from attr import attrs, attrib, asdict

from easy_automation.utils.common import FrozenJson, find_project_root_dir


class SettingLoader:

    def __init__(self, settings_filename='settings'):
        settings_package = 'settings'
        settings_filename = f".{settings_filename}"
        sys.path.append(find_project_root_dir())
        _settings = importlib.import_module(settings_filename, package=settings_package)
        for setting in dir(_settings):
            if setting.isupper():
                value = getattr(_settings, setting)
                setattr(self, setting, FrozenJson(value))

    def merge_from(self, other_settings):
        if not (isinstance(other_settings, SettingLoader)):
            raise RuntimeError("merge object must be an instance of Setting")

        for other_setting in dir(other_settings):
            if other_setting.isupper():
                if other_setting == 'APPS' and other_setting in dir(self):
                    # APPS 下的配置属性 other_settings 存在，self 不存在的，复制到self;
                    # other_settings不存在，self存在，保留self上的
                    app_list = getattr(other_settings, other_setting)
                    app_obj_list = [App(**getattr(setting, "_FrozenJson__data")) for setting in app_list]
                    origin_app_list = getattr(self, other_setting)
                    origin_app_obj_list = [App(**getattr(setting, "_FrozenJson__data")) for setting in origin_app_list]
                    merge_app_obj_list = []
                    app_attr = ['namespace', 'deployment', 'path']
                    for app_obj in app_obj_list:
                        for origin_app_obj in origin_app_obj_list:
                            if app_obj.name == origin_app_obj.name and app_obj.type == origin_app_obj.type:
                                for attr in app_attr:
                                    if getattr(origin_app_obj, attr) is None:
                                        v = getattr(app_obj, attr)
                                        setattr(origin_app_obj, attr, v)
                                merge_app_obj_list.append(origin_app_obj)
                                break
                        else:
                            merge_app_obj_list.append(app_obj)

                    merge_app_list = [asdict(app_obj) for app_obj in merge_app_obj_list]
                    setattr(self, other_setting, FrozenJson(merge_app_list))
                if other_setting not in dir(self):
                    value = getattr(other_settings, other_setting)
                    setattr(self, other_setting, value)

    def merge_to(self, other_settings):
        if not (isinstance(other_settings, SettingLoader)):
            raise RuntimeError("merge object must be an instance of Setting")

        other_settings.merge_from(self)


@attrs
class App:
    name = attrib(default=None)
    namespace = attrib(default=None)
    type = attrib(default="api")
    deployment = attrib(default=None)
    path = attrib(default=None)
    host = attrib(default=None)




