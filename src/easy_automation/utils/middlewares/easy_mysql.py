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
        self._connect = "{} connector".format(connect.db)

    def select_one(self, sql):
        with self.db.cursor(pymysql.cursors.DictCursor) as cur:
            log.debug(f"execute sql: {sql}")
            cur.execute(sql)
            return cur.fetchone()

    def select_all(self, sql):
        with self.db.cursor(pymysql.cursors.DictCursor) as cur:
            log.debug(f"execute sql: {sql}")
            cur.execute(sql)
            return cur.fetchall()

    def _close_connect(self):
        log.debug(f"{self._connect} connect close")
        self.db.close()


class EasyMysql(MiddlewareABC):

    def __init__(self, host, prot, username, password, autocommit=True):
        self._host = host
        self._prot = prot
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
        return self._prot

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
              prot=3306,
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


