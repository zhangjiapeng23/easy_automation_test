#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/14
import copy

import requests

from ..utils.custom_logging import Logs


class RequestBase:
    log = Logs(__name__)
    _session = requests.session()
    _headers = {}

    def send(self, method, url, verify=False, *args, **kwargs):
        params = ""
        for k, v in kwargs.items():
            if params:
                params += ", "
            params += f"{k}={v}"
        self.log.debug('{} {} {}'.format(method, url, params))
        return self._session.request(method, url, headers=self._headers, verify=verify, *args, **kwargs)

    def set_headers(self, headers_dic: dict):
        self._headers = copy.deepcopy(headers_dic)

    def add_header(self, header_dic: dict):
        self._headers.update(header_dic)

    def modify_header(self, key, value):
        self._headers[key] = value

    def delete_header(self, key):
        if key in self._headers.keys():
            self._headers.pop(key)

    def clear_header(self):
        self._headers.clear()