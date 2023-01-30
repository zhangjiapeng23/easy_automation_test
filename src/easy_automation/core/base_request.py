#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/14
import requests

from ..utils.custom_logging import Logs


class RequestBase:
    log = Logs(__name__)

    def __init__(self):
        self._session = requests.session()

    def send(self, method, url, *args, **kwargs):
        self.log.debug('{} {}'.format(method, url))
        return self._session.request(method, url, *args, **kwargs)

