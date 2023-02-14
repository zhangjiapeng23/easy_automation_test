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
        self._settings = _SettingsProxy(env, settings)

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

    def api_url(self, app, path_name):
        if hasattr(self._settings.apps, app):
            app_loader = getattr(self._settings.apps, app)
            path = getattr(app_loader.path, path_name)
            return self._settings['PROJECT_HOST'] + path
        raise RuntimeError(f"Not find {app} project settings")

    def api_url_ip(self, app, path_name):
        if hasattr(self._settings.apps, app):
            app_loader = getattr(self._settings.apps, app)
            path = getattr(app_loader.path, path_name)
            return app_loader.ip + path
        raise RuntimeError(f"Not find {app} project settings")


class _SettingsProxy:

    def __init__(self, env, settings):
        self._settings = settings
        middleware = self._settings.MIDDLEWARE
        apps = self._settings.APPS

        # 初始化注册app
        self._app = AppLoader(apps, env)

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

    @property
    def apps(self):
        return self._app

    def __getitem__(self, item):
        return getattr(self._settings, item)


class _TestDataProxy:

    def __init__(self, testdata):
        self._testdata = testdata
        for key in self._testdata.keys():
            setattr(self, f"_{key}", self._testdata.get(key))

    def case(self, case_name):
        pass

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
