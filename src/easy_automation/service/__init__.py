#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/1/31
import os
import socket
import atexit
import signal
import sys

from flask import Flask

from easy_automation.service.consul_client import ConsulClient
from easy_automation.utils.common import find_project_root_dir
from easy_automation.utils.custom_logging import Logs

log = Logs(__name__)


def create_app(test_config=None):
    service_ids = []
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        _path = find_project_root_dir()
        config_path = os.path.join(_path, 'config.py')
        app.config.from_pyfile(config_path, silent=True)
    else:
        app.config.from_mapping(test_config)

    # 加载特定前缀FLASK_ 的环境变量
    app.config.from_prefixed_env()
    try:
        os.mkdir(app.instance_path)
    except OSError:
        pass

    if not app.config.get('DEBUG'):
        try:
            consul_host = app.config.get('FLASK_CONSUL_HOST')
            consul_port = app.config.get('FLASK_CONSUL_PORT')
            name = app.config.get('FLASK_SERVICE_NAME')
            port = int(app.config.get('FLASK_SERVICE_PORT'))
            tags = app.config.get('FLASK_CONSUL_TAGS')
            ip = socket.gethostbyname(socket.gethostname())
            _ip = ip.split(".")
            _ip = '-'.join(_ip)
            service_id = f"{name}-{_ip}-{port}"
            consul_instance = ConsulClient(host=consul_host, port=consul_port)
            consul_instance.register(name=name, port=port, http_check=f"http://{ip}:{port}/health",
                                     service_id=service_id, address=ip, tags=tags, interval='30s')
            service_ids.append(service_id)
            app.config['CONSUL'] = consul_instance
            log.info(f"consul register success, service-id: {service_id}")
        except Exception as e:
            raise RuntimeError(f"Service register consul fail: {e}")

    from . import cases
    app.register_blueprint(cases.bp)
    from . import health
    app.register_blueprint(health.bp)

    def unregister_consul():
        while len(service_ids) > 0:
            _id = service_ids.pop()
            res = consul_instance.deregister(_id)
            if res:
                log.info(f"service-id: {service_id} unregister consul success")
            else:
                log.warning(f"service-id: {service_id} unregister consul fail")

    def signal_handler(_signal, frame):
        unregister_consul()
        sys.exit(0)

    atexit.register(unregister_consul)
    signal.signal(signal.SIGINT, signal_handler)

    return app



