#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/1/31
import os

from flask import Flask
from easy_automation.service.consul_client import ConsulClient


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_pyfile('./config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.mkdir(app.instance_path)
    except OSError:
        pass

    if not app.config.get('DEBUG'):
        try:
            consul_host = app.config.get('CONSUL_HOST')
            consul_port = app.config.get('CONSUL_PORT')
            name = app.config.get('NAME')
            port = app.config.get('PORT')
            url_prefix = app.config.get('URL_PREFIX')
            tags = app.config.get('CONSUL_TAGS')
            c = ConsulClient(host=consul_host, port=consul_port)
            c.register(name=name, port=port, http_check=f'/api/{url_prefix}/health', tags=tags)
            app.config['CONSUL'] = c
        except Exception as e:
            raise RuntimeError(f"Service register consul fail: {e}")

    from . import cases
    app.register_blueprint(cases.bp)
    from . import health
    app.register_blueprint(health.bp)

    return app