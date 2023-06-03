#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/2/14
import os.path

from kubernetes import config, client

from easy_automation.utils.custom_logging import Logs
from easy_automation.utils.common import find_project_root_dir

setattr(client.Configuration(), 'verify_ssl', False)

log = Logs(log_name="k8s")


def get_pod_ip(self):

    def wrapper(namespace, deployment):
        # 获取对应namespace 下的所有deployment
        deployments = self._appV1.list_namespaced_deployment(namespace=namespace).items
        deployment_obj = None
        ips = []
        for dp in deployments:
            if dp.metadata.name == deployment:
                deployment_obj = dp
                break
        if deployment_obj:
            # 查出对应的端口号
            env_vars = deployment_obj.spec.template.spec.containers[0].env
            for var in env_vars:
                print(var)
                if var.name == 'SERVER_PORT':
                    port = var.value
                    break
            else:
                port = '9083'
            # 查出对应deployment的match_labels
            labels = ""
            for k, v in deployment_obj.spec.selector.match_labels.items():
                if labels:
                    labels += ","
                labels += (k + "=" + v)
            # 通过match_label 找出对应的pod
            pods = self._coreV1.list_namespaced_pod(namespace=namespace, label_selector=labels).items

            # 组装pod的ip和port
            for p in pods:
                ips.append(f"http://{p.status.pod_ip}:{port}")
        return ips

    return wrapper


def get_pod_id_error(*args, **kwargs):
    #  未查找到对应环境的k8s配置文件，将IP地址设置为本地
    return ['http://127.0.0.1']


class Kube:

    def __init__(self, env):
        conf_path = os.path.join(find_project_root_dir(), "settings", "k8s",  env)
        if os.path.exists(conf_path):
            config.load_kube_config(conf_path)
            self._coreV1 = client.CoreV1Api()
            self._appV1 = client.AppsV1Api()
            setattr(self, "get_pod_ip", get_pod_ip(self))
        else:
            log.warning(f"Under this path: {conf_path}, not find k8s config")
            setattr(self, "get_pod_ip", get_pod_id_error)


