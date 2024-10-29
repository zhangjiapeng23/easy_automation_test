#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/2/14
import datetime

from easy_automation.utils.k8s.kube_service import Kube
from easy_automation.utils.custom_logging import Logs
from easy_automation.service.consul_client import ConsulClient

log = Logs(log_name='appLoader')


class AppLoader:
    # 主要负责对所有注册的APP设置服务的ip和port

    def __init__(self, apps: list, env: str, consul_dir: str):
        self._env = env
        self._init_time = datetime.datetime.utcnow().timestamp()
        # 优先用consul 查询ip 模式
        if consul_dir:
            consul_dir = consul_dir.strip("http://").split(":")
            c = ConsulClient(host=consul_dir[0], port=consul_dir[1])
            for app in apps:
                ip, port = c.get_service(app.deployment)
                ip = f"http://{ip}:{port}"
                log.info(f"set app: {app.name} ip: {ip}")
                setattr(app, "ip", ip)
                setattr(self, app.name, app)
        else:
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
