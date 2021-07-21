#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/15

import requests
import os

from .setting import setting
from .exception import CommandError


def update_testcases():
    try:
        WEB_SERVER_HOST = setting.WEB_SERVER_HOST
        TESTCASES_UPLOAD_URL = setting.TESTCASES_UPLOAD_URL
    except AttributeError:
        msg = 'WEB_SERVER_HOST or TESTCASES_UPLOAD_URL not set in settings'
        raise CommandError(msg)

    upload_server = WEB_SERVER_HOST + TESTCASES_UPLOAD_URL
    testcases = []
    testcase_record_file = os.path.join(os.getcwd(), 'testcases_nodeid_record.txt')
    with open(testcase_record_file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            testcase = {}
            testcase['node_id'] = line
            testcases.append(testcase)

    resp = requests.post(url=upload_server, json=testcases)
    print(resp.json())


if __name__ == '__main__':
    update_testcases()