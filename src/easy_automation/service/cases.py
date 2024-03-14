#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2024/3/12
import json

from flask import Blueprint, request
import pytest
import queue
import threading

from easy_automation.utils.loaders.config_loader import ConfigLoader
from easy_automation.utils.loaders.setting_loader import App
from easy_automation.core.plugin import testcases_collector
from easy_automation.utils.custom_logging import Logs

bp = Blueprint('cases', __name__, url_prefix='/cases')

q = queue.Queue()

log = Logs(log_name=__name__)


@bp.get('/sync')
def sync():
    cl = ConfigLoader()
    if hasattr(cl.base_setting, 'APPS'):
        app_list = getattr(cl.base_setting, 'APPS')
        app_obj_list = [App(**getattr(setting, "_FrozenJson__data")) for setting in app_list]
        for app in app_obj_list:
            pytest.main([f"{app.name}_{app.type}_test", '--collect-only', '-q', '--app', app.name,
                         '--type', app.type])
        return json.dumps(list(testcases_collector))
    else:
        return 'no app'


@bp.post('/execute')
def execute():
    data = request.get_json()
    app = data.get("app")
    _type = data.get('type')
    testcases = data.get('testcases')
    q.put((app, _type, testcases))
    return "task add queue"


def worker():
    while True:
        app, _type, testcases = q.get()
        log.info("testcases execute start")
        try:
            pytest.main([*testcases, '--app', app, '--type', _type])
        except Exception as e:
            log.error(e)
        log.info("testcases execute end")


threading.Thread(target=worker, daemon=True).start()