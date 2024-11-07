#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/2/8
import pymysql

from easy_automation.utils.custom_logging import Logs
from easy_automation.utils.middlewares.middleware_abs import MiddlewareABC

log = Logs(log_name="mysql")


class _MysqlConnector:

    def __init__(self, connect: pymysql.Connect):
        self.db = connect
        self._connect = "{} connector".format(connect.db.decode('utf-8'))

    def select_one(self, sql, args=None):
        self.db.ping(reconnect=True)
        with self.db.cursor(pymysql.cursors.DictCursor) as cur:
            if args:
                log.debug(f"execute sql: {sql % args}")
            else:
                log.debug(f"execute sql: {sql}")
            cur.execute(sql, args)
            return cur.fetchone()

    def select_all(self, sql, args=None):
        self.db.ping(reconnect=True)
        with self.db.cursor(pymysql.cursors.DictCursor) as cur:
            if args:
                log.debug(f"execute sql: {sql % args}")
            else:
                log.debug(f"execute sql: {sql}")
            cur.execute(sql, args)
            return cur.fetchall()

    def select_all_tuple(self, sql, args=None):
        self.db.ping(reconnect=True)
        with self.db.cursor() as cur:
            if args:
                log.debug(f"execute sql: {sql % args}")
            else:
                log.debug(f"execute sql: {sql}")
            cur.execute(sql, args)
            return cur.fetchall()

    def execute(self, sql, args=None):
        self.db.ping(reconnect=True)
        with self.db.cursor(pymysql.cursors.DictCursor) as cur:
            if args:
                log.debug(f"execute sql: {sql % args}")
            else:
                log.debug(f"execute sql: {sql}")
            return cur.execute(sql, args)

    def _close_connect(self):
        self.db.ping(reconnect=True)
        log.debug(f"{self._connect} connect close")
        self.db.close()


class EasyMysql(MiddlewareABC):

    def __init__(self, host, port, username, password, autocommit=True):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._autocommit = autocommit

    def get_connect(self, db_name) -> _MysqlConnector:
        return super(EasyMysql, self).get_connect(db_name)

    def _create_connect(self, db_name):
        connect = pymysql.connect(host=self.host, port=self.port, user=self.username, password=self.password,
                                  database=db_name, autocommit=self.autocommit)
        return _MysqlConnector(connect)

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def autocommit(self):
        return self._autocommit


if __name__ == '__main__':
    mysql = EasyMysql(host='pre-us.clxptq1z8dud.rds.cn-north-1.amazonaws.com.cn',
              port=3306,
              username='QA',
              password="webull1688")
    c = mysql.get_connect("wl_auth")
    res1 = c.select_one("select * from wla_user where id=100000732;")
    res2 = c.select_one("select * from wla_permission;")
    c2 = mysql.get_connect("wl_approve")
    res3 = c2.select_one("select * from wla_approve_template;")
    print(res1)
    print(res2)
    print(res3)
    MiddlewareABC.close_all_connect()


