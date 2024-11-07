#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2024/3/12
import json

import requests
from flask import Blueprint, request, current_app
import pytest
import queue
import threading

from easy_automation.utils.loaders.config_loader import ConfigLoader
from easy_automation.utils.loaders.setting_loader import App
from easy_automation.core.plugin import testcases_collector, logger
from easy_automation.utils.custom_logging import Logs
from easy_automation.service.consul_client import ConsulClient


q = queue.Queue()

log = Logs(log_name=__name__)

bp = Blueprint('cases', __name__)


@bp.get('/sync')
def sync():
    cl = ConfigLoader()
    if hasattr(cl.base_setting, 'APPS'):
        app_list = getattr(cl.base_setting, 'APPS')
        app_obj_list = [App(**getattr(setting, "_FrozenJson__data")) for setting in app_list]
        for app in app_obj_list:
            pytest.main([f"{app.name}", '--collect-only', '-q', '--app', app.name,
                         '--type', app.type])
        resp = []
        for case in testcases_collector.values():
            name = case.node_id
            suit = "未命名"
            for label in case.labels:
                if label.get('key') == 'feature' or label.get('key') == 'story':
                    name = label.get('value')
                elif label.get('key') == 'epic':
                    suit = label.get('value')

            app = case.node_id.split("/")[0]
            resp.append({
                'app': app,
                'code': case.node_id,
                'name': name,
                'suit': suit,
                'params': case.params
            })
        return json.dumps(resp, ensure_ascii=False)
    else:
        return 'no app'


@bp.post('/execute')
def execute():
    upload_result_url = None
    try:
        if not current_app.config.get('DEBUG'):
            c: ConsulClient = current_app.config.get('CONSUL')
            ip, port = c.get_service("sRouter2")
            upload_result_url = f'http://{ip}:{port}/api/oa-test/execute-record/update-result'
    except Exception as e:
        log.error(f"获取平台服务地址出错：{e}")
    data = request.get_json()
    app = data.get("app")
    _type = data.get('type')
    testcases = data.get('testcases')
    task_id = data.get('taskId')
    q.put((app, _type, testcases, task_id, upload_result_url))
    return "true"


def worker():
    while True:
        app, _type, testcases, task_id, upload_result_url = q.get()
        log.info(f"taskId: {task_id} execute start")
        try:
            pytest.main([*testcases, '--app', app, '--type', _type, '--easy-log', '1', '--reruns', '2',
                         '--reruns-delay', '3'])
            data = {
                'executeRecordId': task_id,
                'result': json.dumps(logger.test_cases, ensure_ascii=False),
                'passed': logger.passed,
                'failed': logger.failed,
                'error': logger.error,
                'skipped': logger.skipped,
                'total': logger.total,
                'passingRate': logger.passing_rate,
                'duration': logger.duration
            }
            log.info(f"taskId: {task_id} execute end")
            # log.info(logger.test_cases)
            # 上传测试结果数据
            if upload_result_url:
                upload_result(upload_result_url, data)
        except Exception as e:
            log.error(e)
        finally:
            logger.clear_data()


def upload_result(url, data):
    log.info(f"上传测试结果：{url}")
    resp = requests.post(url=url, json=data)
    if resp.status_code == 200:
        log.info(f"taskId: {data.get('executeRecordId')} result upload success, data: {data}")
    else:
        log.error(f"taskId: {data.get('executeRecordId')} result upload failed, msg: {resp.text}, data: {data}")


threading.Thread(target=worker, daemon=True).start()

