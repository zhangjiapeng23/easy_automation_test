#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/19
import hashlib
import socket
import threading
import uuid
import keyword
import os
import time
from collections import abc
from functools import wraps
import json

import pytest

from .exception import PathFindError


class Singleton(type):

    def __init__(cls, *args, **kwargs):
        cls._instances = {}
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if args[0] not in cls._instances:
            cls._instances[args[0]] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[args[0]]


def singleton(cls):
    _instance = {}

    def inner(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]
    return inner


class FrozenJson:

    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self.__data = {}
        for key, val in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
            self.__data[key] = val

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            if name not in self.__data:
                msg = "'{}' object has no attribute '{}'"
                raise AttributeError(msg.format(self.__class__.__name__, name))
            else:
                return FrozenJson(self.__data[name])


def http_retry(retry_times=3):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal retry_times
            while retry_times > 0:
                resp = func(*args, **kwargs)
                if resp.status_code != 201:
                    retry_times -= 1
                    time.sleep(10)
                    continue
                else:
                    break
            return resp

        return wrapper

    return decorator


def find_project_root_dir():
    cur_dir = os.getcwd()
    while True:
        root, _, files = next(os.walk(cur_dir))
        if 'manage.py' in files:
            return root
        else:
            higher_dir = os.path.dirname(cur_dir)
            if higher_dir == cur_dir:
                raise PathFindError
            else:
                cur_dir = higher_dir


def _easy_parametrize(param):

    def decorator(func):
        keys, values, ids = param

        @wraps(func)
        @pytest.mark.parametrize(keys, values, ids=ids)
        def wrap(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        return wrap

    return decorator


class easy_parametrize:

    def __init__(self, *params):
        self.keys = []
        self.values = []
        self.ids = []

        # 递归传入的列表参数，返回笛卡尔集
        def recur(keys, values, ids, cur_keys: list, cur_values: list, cur_ids: list, n):
            if n == len(params):
                if len(keys) == 0:
                    # keys 只需一次即可确定
                    keys.extend(cur_keys)
                if len(cur_values) > 1:
                    _new = []
                    # 多组值时合并为一个扁平序列，如：[(1, 2), (a, b)] => [1, 2, a, b]
                    for v in cur_values:
                        for _v in v:
                            _new.append(_v)
                    values.append(tuple(_new))
                else:
                    _v = cur_values[0]
                    # 区分是 (a,)和(a, b), 为 （a,) 直接返回 a
                    if len(_v) == 1:
                        _v = _v[0]
                    values.append(_v)
                ids.append("_".join(cur_ids))
            else:
                param = params[n]
                _key, _values, _ids = param
                for _value, _id in zip(_values, _ids):
                    cur_keys.append(_key)
                    cur_values.append(_value)
                    cur_ids.append(_id)
                    recur(keys, values, ids, cur_keys, cur_values, cur_ids, n+1)
                    cur_keys.pop()
                    cur_values.pop()
                    cur_ids.pop()

        cur_keys = []
        cur_values = []
        cur_ids = []
        recur(self.keys, self.values, self.ids, cur_keys, cur_values, cur_ids, 0)

    def __call__(self, func):
        keys = ",".join(self.keys)
        values = self.values
        ids = self.ids

        @wraps(func)
        @pytest.mark.parametrize(keys, values, ids=ids)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper


def md5(*args):
    m = hashlib.md5()
    for arg in args:
        if not isinstance(arg, bytes):
            if not isinstance(arg, str):
                arg = repr(arg)
        arg = arg.encode('utf-8')
        m.update(arg)
    return m.hexdigest()


def uuid4():
    return str(uuid.uuid4())


def now():
    return int(round(1000 * time.time()))


def thread_tag():
    return f"{os.getpid()}-{threading.current_thread().name}"


def host_tag():
    return socket.gethostname()


class TearDown:

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self.__kwargs = kwargs

    def __enter__(self):
        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._func(*self._args, **self.__kwargs)
        return False


class Assert:
    def JsonEqu(self, exp_body, act_body):
        assert json.dumps(exp_body, sort_keys=True) == json.dumps(act_body, sort_keys=True)

    def JsonContains(self, exp_sql, act_sql, remove_key_boe=None):
        if remove_key_boe is None:
            contains_b = all(item in exp_sql.items() for item in act_sql.items())
            assert contains_b is True
        else:
            for key in remove_key_boe:
                act_sql.pop(key, None)
                contains_b = all(item in exp_sql.items() for item in act_sql.items())
                assert contains_b is True

    def detailjson_removeKey(self, data, remove_keys):
        for key in remove_keys:
            data.pop(key, None)
        return data
