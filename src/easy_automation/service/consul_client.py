#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2024/8/30
import json
import random

import requests
from consulate import Consul


class ConsulClient:

    def __init__(self, host=None, port=None, token=None):
        self._host = host
        self._port = port
        self._token = token
        self._consul = Consul(host=host, port=port, token=token)

    def register(self, name, port, http_check, service_id=None, address=None, tags=None, interval=None):
        self.consul.agent.service.register(name=name, service_id=service_id, address=address, port=port, tags=tags,
                                           interval=interval, httpcheck=http_check)

    def deregister(self, service_id):
        self.consul.agent.service.deregister(service_id)
        self.consul.agent.check.deregister(service_id)

    def get_service(self, name):
        url = f"http://{self.host}:{self.port}/v1/catalog/service/{name}"
        data_center_resp = requests.get(url)
        if data_center_resp.status_code != 200:
            raise RuntimeError('can not connect to consul')
        data_list = json.loads(data_center_resp.text)
        dc_set = set()
        for s in data_list:
            dc_set.add(s.get('Datacenter'))
        service_list = []
        for dc in dc_set:
            url = f"http://{self.host}:{self.port}/v1/health/service/{name}?dc={dc}"
            if self.toke:
                url += f"&token={self.token}"
            resp = requests.get(url)
            if resp.status_code != 200:
                raise RuntimeError('can not connect to consul')
            service_list_data = json.loads(resp.text)
            for s in service_list_data:
                status = s.get('Checks')[0].get('Status')
                if status == 'passing':
                    address = s.get('Service').get('Address')
                    port = s.get('Service').get('Port')
                    service_list.append({'address': address, 'port': port})

        if not service_list:
            raise RuntimeError('No service can be used')
        else:
            service = service_list[random.randint(0, len(service_list) - 1)]
            return service['address'], int(service['port'])

    @property
    def consul(self):
        return self._consul

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def token(self):
        return self._token

