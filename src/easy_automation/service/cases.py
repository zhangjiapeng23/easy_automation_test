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
            pytest.main([f"{app.name}_{app.type}_test", '--collect-only', '-q', '--app', app.name,
                         '--type', app.type])
        resp = []
        for code, name in testcases_collector:
            app = code.split("/")[0]
            resp.append({
                'app': app,
                'code': code,
                'name': name
            })
        return json.dumps(resp, ensure_ascii=False)
    else:
        return 'no app'


@bp.post('/execute')
def execute():
    upload_result_url = None
    try:
        if not current_app.config.get('DEBUG'):
            service_name = current_app.config.get('FLASK_SERVICE_NAME')
            c: ConsulClient = current_app.config.get('CONSUL')
            ip, port = c.get_service(service_name)
            upload_result_url = f'http://{id}:{port}/api/result/upload'
    except Exception as e:
        log.error(f"获取平台服务地址出错：{e}")
    data = request.get_json()
    app = data.get("app")
    _type = data.get('type')
    testcases = data.get('testcases')
    task_id = data.get('taskId')
    q.put((app, _type, testcases, task_id, upload_result_url))
    return "task add queue"


def worker():
    while True:
        app, _type, testcases, task_id, upload_result_url = q.get()
        log.info(f"taskId: {task_id} execute start")
        try:
            pytest.main([*testcases, '--app', app, '--type', _type, '--easy-log', '1'])
            data = {
                'taskId': task_id,
                'result': logger.test_cases
            }
            print(data)
            log.info(f"taskId: {task_id} execute end")

            # 上传测试结果数据
            if upload_result_url:
                upload_result(upload_result_url, data)
        except Exception as e:
            log.error(e)
        finally:
            logger.clear_data()


def upload_result(url, data):
    resp = requests.post(url=url, json=data)
    if resp.status_code == 200:
        log.info(f"taskId: {data.get('taskId')} result upload success")
    else:
        log.error(f"taskId: {data.get('taskId')} result upload failed, msg: {resp.text}")


threading.Thread(target=worker, daemon=True).start()

