#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/2/8
import abc
from abc import ABCMeta


class MiddlewareABC(metaclass=ABCMeta):

    _db_connect = {}

    def get_connect(self, db_name):
        if db_name not in self._db_connect.keys():
            connect = self._create_connect(db_name)
            self._db_connect[db_name] = connect
        return self._db_connect[db_name]

    @abc.abstractmethod
    def _create_connect(self, db_name):
        raise NotImplementedError("create connect method is not implemented!")








