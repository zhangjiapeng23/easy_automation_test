#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/2/9
import redis

from easy_automation.utils.custom_logging import Logs
from easy_automation.utils.middlewares.middleware_abs import MiddlewareABC

log = Logs(log_name="mysql")


class _RedisConnector:

    def __init__(self, connect: redis.Redis):
        self.db = connect
        self._connect = "{} connector".format(connect)

    def get(self, name):
        log.debug(f"get key: {name}")
        return self.db.get(name)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        log.debug(f"set key {name} {value}")
        return self.db.set(name=name, value=value, ex=ex, px=px, nx=nx)

    def __getattr__(self, item):
        if hasattr(self.db, item):
            return getattr(self.db, item)
        raise RuntimeError(f"Redis does not have this attribute: {item}")

    def _close_connect(self):
        log.debug(f"{self._connect} connect close")
        self.db.close()


class EasyRedis(MiddlewareABC):

    def __init__(self, host, prot, password="", decode_responses=True):
        self._host = host
        self._prot = prot
        self._password = password
        self._decode_responses = decode_responses

    def get_connect(self, db_name) -> _RedisConnector:
        return super(EasyRedis, self).get_connect(db_name)

    def _create_connect(self, db_name):
        connect = redis.Redis(host=self.host, port=self.port, db=db_name, password=self.password,
                              decode_responses=self.decode_responses)
        return _RedisConnector(connect)

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._prot

    @property
    def password(self):
        return self._password

    @property
    def decode_responses(self):
        return self._decode_responses

if __name__ == '__main__':
    r = EasyRedis(host='k8s-middlewa-dcus1red-e9aab31110-d4b6c6e8f6aae0bf.elb.cn-north-1.amazonaws.com.cn',
                      prot=6379)
    c = r.get_connect(4)
    res1 = c.get('auth.token.100000732')
    res2 = c.get('auth.token.refresh.100001418')
    c2 = r.get_connect(6)
    res3 = c2.get("operation.user.1990004214.pop.count")
    print(res1)
    print(res2)
    print(res3)
    MiddlewareABC.close_all_connect()


