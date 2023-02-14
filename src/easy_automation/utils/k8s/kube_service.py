#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/2/14
import os.path

from kubernetes import config, client

from easy_automation.utils.common import find_project_root_dir

setattr(client.Configuration(), 'verify_ssl', False)


class Kube:

    def __init__(self, env):
        conf_path = os.path.join(find_project_root_dir(), "settings", "k8s",  env)
        config.load_kube_config(conf_path)
        self._coreV1 = client.CoreV1Api()
        self._appV1 = client.AppsV1Api()

    def get_pod_ip(self, namespace, deployment):
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
            port = deployment_obj.spec.template.spec.containers[0].ports[0].container_port
            labels = ""
            # 查出对应deployment的match_labels
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
