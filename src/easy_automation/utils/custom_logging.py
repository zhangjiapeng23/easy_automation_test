#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/14
# import datetime

import logging
import logging.handlers
import os


class Logs:

    def __init__(self, log_name='easy-automation'):
        self._log = logging.getLogger(log_name)
        formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s'
                                      ': %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.INFO)

        logs_dir = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)
        log_file = os.path.join(logs_dir, 'log.log')
        fh = logging.handlers.RotatingFileHandler(filename=log_file, mode='a', maxBytes=8*1024*20)
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)

        self._log.setLevel(logging.DEBUG)
        self._log.addHandler(sh)
        self._log.addHandler(fh)

        # _datetime = datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")
        # msg = "="*15 + _datetime + "="*15
        # self.info(msg)

    def debug(self, msg, *args, **kwargs):
        self._log.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log.critical(msg, *args, **kwargs)







