import os
import time
from typing import List

import pytest
from easy_automation.utils.custom_logging import Logs
from easy_automation.utils.loaders import ConfigLoader
from easy_automation.utils.middlewares.middleware_abs import MiddlewareABC

# 装载全局配置和测试数据对象
context: ConfigLoader = None

log = Logs()
root_dir = os.path.join(os.path.dirname(__file__), "..")


def pytest_addoption(parser):
    # add run evn option
    parser.addoption("--env", action="store", default="pre", help="指定测试运行环境")
    # add app name option
    parser.addoption("--app", action="store", required=True, help="指定测试APP")
    # add test type option
    parser.addoption("--type", action="store", required=True, choices=('web', 'api'), help="指定测试类型")


def pytest_configure(config):
    global context
    env = config.getoption("--env")
    app = config.getoption("--app")
    test_type = config.getoption("--type")
    context = ConfigLoader(app, env, test_type)
    # 添加清理任务：关闭中间件连接
    config.add_cleanup(disconnect_middleware)


def disconnect_middleware():
    MiddlewareABC.close_all_connect()


def pytest_collection_modifyitems(
        session: "Session", config: "Config", items: List["Item"]) -> None:
    """Called after collection has been performed. May filter or re-order
       the items in-place.

       :param pytest.Session session: The pytest session object.
       :param _pytest.config.Config config: The pytest config object.
       :param List[pytest.Item] items: List of item objects.
       """
    for item in items:
        item.name = item.name.encode('utf-8').decode('unicode-escape')
        item._nodeid = item.nodeid.encode('utf-8').decode('unicode-escape')

    # nodeid_record_path = os.path.join(root_dir, "testcases_nodeid_record.txt")

    # def clean_node_id(node_id):
    #     rule = re.compile(r'(?P<node_id>[^\[\]]+)(?P<param>\[*.*\]*)')
    #     res = rule.match(node_id._nodeid)
    #     node_id = res.group('node_id')
    #     return node_id

    # clean_nodeid = list(set(map(clean_node_id, items)))
    # with open(nodeid_record_path, 'w', encoding='utf-8') as f:
    #     for nodeid in clean_nodeid:
    #         f.write(nodeid+'\n')
    #         log.debug(nodeid)


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