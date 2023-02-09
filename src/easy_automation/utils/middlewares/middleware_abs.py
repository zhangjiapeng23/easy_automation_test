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
        for i in cls._db_connect.values():
            if hasattr(i, '_close_connect'):
                getattr(i, '_close_connect')()

    @abc.abstractmethod
    def _create_connect(self, db_name):
        raise NotImplementedError("create connect method is not implemented!")











