#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2024/1/25
import os
import re
import time
from typing import List

import allure_commons
import pytest

from easy_automation.utils.custom_logging import Logs
from easy_automation.utils.loaders.config_loader import ConfigLoader
from easy_automation.utils.middlewares.middleware_abs import MiddlewareABC
from easy_automation.report.listener import EasyListener
from easy_automation.report.logger import MemoryLogger

# 装载全局配置和测试数据对象
context: ConfigLoader = ConfigLoader()
test_listener: EasyListener = None
logger: MemoryLogger = None
testcases_collector = set()

log = Logs()
root_dir = os.path.join(os.path.dirname(__file__), "..")


def cleanup_factory(plugin):
    def clean_up():
        name = allure_commons.plugin_manager.get_name(plugin)
        allure_commons.plugin_manager.unregister(name=name)
    return clean_up


def pytest_addoption(parser):
    # add run evn option
    parser.addoption("--env", action="store", default="pre", help="指定测试运行环境")
    # add app name option
    parser.addoption("--app", action="store", required=True, help="指定测试APP")
    # add test type option
    parser.addoption("--type", action="store", required=True, choices=('web', 'api'), help="指定测试类型")
    # add collect log optoin
    parser.addoption("--easy-log", action='store', default='0', choices=('0', '1'), help="采集日志数据")


def pytest_configure(config):
    global context
    global test_listener
    global logger
    allure_report_dir = config.option.allure_report_dir
    env = config.getoption("--env")
    app = config.getoption("--app")
    test_type = config.getoption("--type")
    log_flag =  config.getoption("--easy-log")
    context.reload_init(app, env, test_type)
    # 添加清理任务：关闭中间件连接
    config.add_cleanup(disconnect_middleware)
    # 添加输出report log任务
    config.add_cleanup(print_report)
    # 注册 report listener 插件
    if not allure_report_dir and log_flag == '1':
        test_listener = EasyListener(config)
        config.pluginmanager.register(test_listener, 'easy_listener')
        allure_commons.plugin_manager.register(test_listener)
        config.add_cleanup(cleanup_factory(test_listener))
        # 注册 report logger 插件
        logger = MemoryLogger()
        allure_commons.plugin_manager.register(logger)
        config.add_cleanup(cleanup_factory(logger))


def disconnect_middleware():
    MiddlewareABC.close_all_connect()


def print_report():
    if logger:
        print(logger.test_cases)
        print(logger.test_containers)
        print(logger.attachments)


def pytest_collection_modifyitems(session: "Session", config: "Config", items: List["Item"]) -> None:
    """Called after collection has been performed. May filter or re-order
       the items in-place.

       :param pytest.Session session: The pytest session object.
       :param _pytest.config.Config config: The pytest config object.
       :param List[pytest.Item] items: List of item objects.
       """
    for item in items:
        item.name = item.name.encode('utf-8').decode('unicode-escape')
        item._nodeid = item.nodeid.encode('utf-8').decode('unicode-escape')

    def clean_node_id(node_id):
        rule = re.compile(r'(?P<node_id>[^\[\]]+)(?P<param>\[*.*\]*)')
        res = rule.match(node_id._nodeid)
        node_id = res.group('node_id')
        return node_id

    testcases_collector.update(map(clean_node_id, items))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    result = {}
    passed = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    failed = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    error = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    skipped = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    total = passed + failed + error + skipped
    passed_rate = '%.2f' % (passed / total * 100) + '%' if total > 0 else 0
    duration = time.time() - terminalreporter._sessionstarttime
    result_format = 'total: {}, passed: {}, failed: {}, error: {}, skipped: {}, passed_rate: {}, duration: {}'
    log.info(result_format.format(total, passed, failed, error, skipped, passed_rate, duration))
    result['testcases_total'] = total
    result['passed'] = passed
    result['failed'] = failed
    result['error'] = error
    result['skipped'] = skipped
    result['passing_rate'] = passed_rate
    result['duration'] = round(duration, 2)