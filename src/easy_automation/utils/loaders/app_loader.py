#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/2/14

from easy_automation.utils.k8s.kube_service import Kube


class AppLoader:

    def __init__(self, apps: list, env: str):
        self._env = env
        for app in apps:
            ip = Kube(env).get_pod_ip(namespace=app.namespace, deployment=app.deployment)[0]
            setattr(app, "ip", ip)
            setattr(self, app.name, app)

    @property
    def env(self):
        return self._env



