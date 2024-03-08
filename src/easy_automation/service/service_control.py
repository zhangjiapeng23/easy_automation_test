#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/1/31

import asyncio
import json
import threading
import queue
from abc import ABC

import pytest
import tornado.web

from easy_automation.utils.loaders.config_loader import ConfigLoader
from easy_automation.utils.loaders.setting_loader import App
from easy_automation.core.plugin import testcases_collector
from easy_automation.utils.custom_logging import Logs

log = Logs(log_name="service")

q = queue.Queue()


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("hello world")


class TestApiHandler(tornado.web.RequestHandler):

    def get(self):
        data = [{"value": 1, "label": "james"}, {"value": 2, "label": "zhang"},
                {"value": 3, "label": "peng"}]
        self.write(json.dumps(data))


class TestCaseSyncHandler(tornado.web.RequestHandler, ABC):

    def get(self):
        cl = ConfigLoader()
        if hasattr(cl.base_settings, 'APPS'):
            app_list = getattr(cl.base_settings, 'APPS')
            app_obj_list = [App(**getattr(setting, "_FrozenJson__data")) for setting in app_list]
            for app in app_obj_list:
                pytest.main([f"{app.name}_{app.type}_test", '--collect-only', '-q', '--app', app.name,
                             '--type', app.type])
            self.write(json.dumps(list(testcases_collector)))
        else:
            self.write("no app")


class TestCaseExecute(tornado.web.RequestHandler, ABC):

    def post(self):
        body = json.loads(self.request.body.decode('utf-8'))
        app = body.get("app")
        _type = body.get('type')
        testcases = body.get('testcases')
        q.put((app, _type, testcases))
        self.write("task add queue")


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/testApi", TestApiHandler),
            (r"/testcase/sync", TestCaseSyncHandler),
            (f"/testcase/execute", TestCaseExecute)
        ]
    )


async def start_service(port: int):
    app = make_app()
    app.listen(port)
    await asyncio.Event().wait()


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


if __name__ == '__main__':
    asyncio.run(start_service(9999))

