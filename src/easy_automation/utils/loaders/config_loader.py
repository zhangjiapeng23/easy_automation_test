#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/1/30

import os.path

from easy_automation.utils.common import find_project_root_dir
from easy_automation.utils.loaders.yaml_loader import YamlLoader
from easy_automation.utils.loaders.setting_loader import SettingLoader


class ConfigLoader:
    """
    加载对应环境，app的 setting 和 testdata 数据
    """

    def __init__(self, app, env, test_type):
        app_name = f"{app}_{test_type}_test"
        testdata_filename = "testdata.yaml"
        settings_filename = "settings"
        root_dir = find_project_root_dir()

        origin_testdata_dir = os.path.join(root_dir, app_name, 'testdata', testdata_filename)
        origin_settings_filename = settings_filename

        if env:
            testdata_filename = f"{env}_{testdata_filename}"
            settings_filename = f"{env}_{settings_filename}"
        testdata_dir = os.path.join(root_dir, app_name, 'testdata', testdata_filename)

        # 初始化setting
        origin_settings = SettingLoader(origin_settings_filename)
        settings = SettingLoader(settings_filename)
        settings.merge_from(origin_settings)
        self._settings = _SettingsProxy(settings)

        # 初始化testdata
        origin_testdata = YamlLoader(origin_testdata_dir)
        testdata = YamlLoader(testdata_dir)
        testdata.merge_from(origin_testdata)
        self._testdata = _TestDataProxy(testdata)

    @property
    def testdata(self):
        return self._testdata

    @property
    def settings(self):
        return self._settings

    def api_url(self, path_name):
        return self._settings['PROJECT_HOST'] + self.testdata.path(path_name)


class _SettingsProxy:

    def __init__(self, settings):
        self._settings = settings

    def get_mysql_connect(self, db_name):
        pass

    def get_redis_connect(self, db_name):
        pass

    def __getitem__(self, item):
        return getattr(self._settings, item)


class _TestDataProxy:

    def __init__(self, testdata):
        self._testdata = testdata
        for key in self._testdata.keys():
            setattr(self, f"_{key}", self._testdata.get(key))

    def case(self, case_name):
        pass

    def path(self, path_name):
        return getattr(self, "_path").get(path_name)

    def account(self, account_name):
        account = getattr(self, "_account").get(account_name)

        if isinstance(account, list):
            account_values = []
            ids = []
            account_keys = ", ".join((k for k in account[0].keys() if k != 'ids'))
            for i in account:
                tuple_value = []
                for k in i.keys():
                    if k == 'ids':
                        ids.append(i[k])
                    else:
                        tuple_value.append(i[k])
            account_values.append(tuple(tuple_value))
        else:
            account_keys = ", ".join((k for k in account.keys() if k != 'ids'))
            account_values = [tuple(account[k] for k in account.keys() if k != 'ids')]
            ids = [account[k] for k in account.values() if k == 'ids']
        return account_keys, account_values, ids
