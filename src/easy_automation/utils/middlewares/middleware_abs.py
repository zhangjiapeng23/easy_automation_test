#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/2/8
import abc
from abc import ABCMeta


class MiddlewareABC(metaclass=ABCMeta):

    _db_connect = {}

    def get_connect(self, db_name):
        if db_name not in self.__class__._db_connect.keys():
            connect = self._create_connect(db_name)
            self.__class__._db_connect[db_name] = connect
        return self.__class__._db_connect[db_name]

    @classmethod
    def close_all_connect(cls):
        db_connect_key = []
        for k, v in cls._db_connect.items():
            if hasattr(v, '_close_connect'):
                getattr(v, '_close_connect')()
                db_connect_key.append(k)
        for k in db_connect_key:
            cls._db_connect.pop(k)

    @abc.abstractmethod
    def _create_connect(self, db_name):
        raise NotImplementedError("create connect method is not implemented!")
