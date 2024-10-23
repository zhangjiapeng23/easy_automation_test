#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/2/14
import datetime

from easy_automation.utils.k8s.kube_service import Kube
from easy_automation.utils.custom_logging import Logs

log = Logs(log_name='appLoader')


class AppLoader:

    def __init__(self, apps: list, env: str):
        self._env = env
        self._init_time = datetime.datetime.utcnow().timestamp()
        for app in apps:
            ip = Kube(env).get_pod_ip(namespace=app.namespace, deployment=app.deployment)[0]
            log.info(f"set app: {app.name} ip: {ip}")
            setattr(app, "ip", ip)
            setattr(self, app.name, app)

    @property
    def is_expired(self):
        # 大于10分钟认为过期
        return datetime.datetime.utcnow().timestamp() - self._init_time > 10 * 60

    @property
    def env(self):
        return self._env
