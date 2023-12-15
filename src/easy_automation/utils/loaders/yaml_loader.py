#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/14
import os

import yaml

from easy_automation.utils.common import Singleton, FrozenJson, find_project_root_dir


class YamlLoader(metaclass=Singleton):
    _yaml_file_loader = {}

    def __init__(self, yaml_file: str):
        '''
        yaml_file 需传递从app module下到testdata.yml的全路径，如 /am_api_test/testdata/testdata.yml
        :param yaml_file:
        '''
        yaml_file = os.path.join(find_project_root_dir(), yaml_file)
        if not (yaml_file.endswith('.yaml') or yaml_file.endswith('.yml')):
            raise TypeError('Only support parse yaml format file.')
        if not os.path.isfile(yaml_file):
            raise FileNotFoundError(f'No such file or directory: {yaml_file}')

        if yaml_file not in self._yaml_file_loader:
            with open(yaml_file, 'r', encoding='utf-8') as fp:
                self._yaml_file_loader[yaml_file] = yaml.safe_load(fp)

        self._yaml_loader = self._yaml_file_loader[yaml_file]
        self._data = FrozenJson(self._yaml_loader)

    @property
    def data(self):
        '''
        access data through properties.
        :return:
        '''
        return self._data

    def get(self, args):
        return self._yaml_loader.get(args)

    def merge_from(self, other_yaml_loader):
        if not (isinstance(other_yaml_loader, YamlLoader)):
            raise RuntimeError("merge object must be an instance of YamlLoader")

        if other_yaml_loader._yaml_loader:
            for other_key in other_yaml_loader._yaml_loader.keys():
                if other_key not in self._yaml_loader.keys():
                    self._yaml_loader[other_key] = other_yaml_loader._yaml_loader.get(other_key)

        self._data = FrozenJson(self._yaml_loader)

    def merge_to(self, other_yaml_loader):
        if not (isinstance(other_yaml_loader, YamlLoader)):
            raise RuntimeError("merge object must be an instance of YamlLoader")

        if other_yaml_loader._yaml_loader:
            for other_key in other_yaml_loader._yaml_loader.keys():
                self._yaml_loader[other_key] = other_yaml_loader._yaml_loader.get(other_key)

        self._data = FrozenJson(self._yaml_loader)

    def __getitem__(self, args):
        return self._yaml_loader[args]

    def __getattr__(self, item):
        if hasattr(self._yaml_loader, item):
            return getattr(self._yaml_loader, item)
        if item == "keys":
            return lambda :[]

        raise AttributeError(f"{self.__class__.__name__} does not hava '{item}' attribute.")


if __name__ == '__main__':
    with open("D:\下载\pre_test.yaml") as f:
        a = yaml.safe_load(f)
        for i in a.keys():
            print(i)
        c = a.get("apiVersion")
        print(c)
        print(a)

