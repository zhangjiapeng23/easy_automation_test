#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/1/30

import os.path

from easy_automation.utils.common import find_project_root_dir
from easy_automation.utils.loaders.yaml_loader import YamlLoader
from easy_automation.utils.loaders.setting_loader import SettingLoader
from easy_automation.utils.loaders.app_loader import AppLoader
from easy_automation.utils.middlewares.easy_mysql import EasyMysql, _MysqlConnector
from easy_automation.utils.middlewares.easy_redis import EasyRedis, _RedisConnector
from easy_automation.utils.custom_faker import CustomFaker


class ConfigLoader:
    """
    加载对应环境，app的 setting 和 testdata 数据
    """
    TESTDATA_FILENAME = "testdata.yaml"
    SETTINGS_FILENAME = "settings"

    def __init__(self, app=None, env=None, test_type=None):
        self._testdata = _TestData()
        self._settings = None
        self._app_setting = None
        if all((app, env, test_type)):
            self._init(app, env, test_type)

    def reload_init(self, app, env, test_type):
        self._init(app, env, test_type)

    def _init(self, app, env, test_type):
        app_name = f"{app}_{test_type}_test"
        root_dir = find_project_root_dir()
        origin_testdata_dir = os.path.join(root_dir, app_name, 'testdata', self.TESTDATA_FILENAME)
        settings_filename = f"{env}_{self.SETTINGS_FILENAME}"
        testdata_dir = os.path.join(root_dir, app_name, 'testdata', f"{env}")

        # 初始化setting
        base_settings = SettingLoader(self.SETTINGS_FILENAME)
        settings = SettingLoader(settings_filename)
        settings.merge_from(base_settings)

        if self.app_setting is None or self.app_setting.env != env:
            # 初始化APP setting
            self._app_setting = AppLoader(settings.APPS, env)

        self._settings = _SettingsProxy(settings)

        # 初始化testdata
        origin_testdata = YamlLoader(origin_testdata_dir)
        setattr(self._testdata, 'testdata', _TestDataProxy(origin_testdata))
        testdata_filename_dict = {}
        for _, _, files in os.walk(testdata_dir):
            for file in files:
                file_name = file.split(".")[0]
                testdata_filename_dict[file_name] = os.path.join(testdata_dir, file)
        for k, v in testdata_filename_dict.items():
            testdata = YamlLoader(v)
            testdata.merge_from(origin_testdata)
            setattr(self._testdata, k, _TestDataProxy(testdata))

    @property
    def testdata(self):
        return self._testdata

    @property
    def settings(self):
        return self._settings

    @property
    def app_setting(self):
        return self._app_setting

    def api_url(self, app, path_name):
        if hasattr(self.app_setting, app):
            app_loader = getattr(self.app_setting, app)
            path = getattr(app_loader.path, path_name)
            if hasattr(app_loader, 'host') and getattr(app_loader, 'host') is not None:
                return getattr(app_loader, 'host') + path
            return self._settings['PROJECT_HOST'] + path
        raise RuntimeError(f"Not find {app} project settings")

    def api_url_ip(self, app, path_name):
        if hasattr(self.app_setting, app):
            app_loader = getattr(self.app_setting, app)
            path = getattr(app_loader.path, path_name)
            return app_loader.ip + path
        raise RuntimeError(f"Not find {app} project settings")

    def api_url_custom_host(self, app, path_name, host):
        if hasattr(self.app_setting, app):
            app_loader = getattr(self.app_setting, app)
            path = getattr(app_loader.path, path_name)
            return host + path
        raise RuntimeError(f"Not find {app} project settings")


class _SettingsProxy:

    def __init__(self, settings):
        self._settings = settings
        middleware = self._settings.MIDDLEWARE

        # 初始化mysql代理对象
        if hasattr(middleware, 'mysql'):
            host = middleware.mysql.host
            port = middleware.mysql.port
            username = middleware.mysql.username
            password = middleware.mysql.password
            self._mysql = EasyMysql(host=host, port=port, username=username, password=password)
        else:
            self._mysql = None

        # 初始化redis代理对象
        if hasattr(middleware, 'redis'):
            host = middleware.redis.host
            port = middleware.redis.port
            password = middleware.redis.password
            self._redis = EasyRedis(host=host, port=port, password=password)
        else:
            self._redis = None

    def get_mysql_connect(self, db_name) -> _MysqlConnector:
        if self._mysql:
            return self._mysql.get_connect(db_name)
        raise RuntimeError("Not set mysql config")

    def get_redis_connect(self, db_name) -> _RedisConnector:
        if self._redis:
            return self._redis.get_connect(db_name)
        raise RuntimeError("Not set redis config")

    def __getitem__(self, item):
        return getattr(self._settings, item)


class _TestDataProxy:

    def __init__(self, testdata):
        self._testdata = testdata
        if self._testdata:
            for key in self._testdata.keys():
                setattr(self, f"_{key}", self._testdata.get(key))

    def case(self, case_name):
        case = getattr(self, "_case").get(case_name)
        return self._parse_data(case)

    def account(self, account_name):
        account = getattr(self, "_account").get(account_name)
        return self._parse_data(account)

    def fake(self, name):
        faker = CustomFaker()
        fake = getattr(self, '_fake').get(name)
        if isinstance(fake, list):
            data_values = []
            ids = []
            data_keys = ", ".join((k for k in fake[0].keys() if k != 'ids'))
            for i in fake:
                tuple_value = []
                for k in i.keys():
                    if k == 'ids':
                        ids.append(i[k])
                    else:
                        # 通过配置的值去获取一个模拟值
                        v = getattr(faker, i[k])
                        if callable(v):
                            v = v()
                        tuple_value.append(v)
                data_values.append(tuple(tuple_value))
        else:
            data_keys = ", ".join((k for k in fake.keys() if k != 'ids'))
            tuple_value = []
            ids = []
            for k in fake.keys():
                if k == 'ids':
                    ids.append(fake[k])
                else:
                    v = getattr(faker, fake[k])
                    if callable(v):
                        v = v()
                    tuple_value.append(v)
            data_values = tuple(tuple_value)
        return data_keys, data_values, ids

    @staticmethod
    def _parse_data(data):
        if isinstance(data, list):
            data_values = []
            ids = []
            data_keys = ", ".join((k for k in data[0].keys() if k != 'ids'))
            for i in data:
                tuple_value = []
                for k in i.keys():
                    if k == 'ids':
                        ids.append(i[k])
                    else:
                        tuple_value.append(i[k])
                data_values.append(tuple(tuple_value))
        else:
            data_keys = ", ".join((k for k in data.keys() if k != 'ids'))
            tuple_value = []
            ids = []
            for k in data.keys():
                if k == 'ids':
                    ids.append(data[k])
                else:
                    tuple_value.append(data[k])
            data_values = tuple(tuple_value)
        return data_keys, data_values, ids

    def _wrapper(self, _item):

        def inner(name):
            data = getattr(self, _item).get(name)
            return self._parse_data(data)

        return inner

    def __getattr__(self, item):
        _item = "_" + item
        if hasattr(self, _item):
            return self._wrapper(_item)

        raise AttributeError(f"{self.__class__.__name__} does not hava '{item}' attribute.")


class _TestData:
    pass

