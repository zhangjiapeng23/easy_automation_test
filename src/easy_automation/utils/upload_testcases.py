#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/15

import requests
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from setting import WEB_SERVER_HOST, TESTCASES_UPLOAD_URL, PROJECT_NAME


root_dir = os.path.join(os.path.dirname(__file__), '..')


def update_testcases():
    upload_server = WEB_SERVER_HOST + TESTCASES_UPLOAD_URL
    testcases = []
    testcase_record_file = os.path.join(root_dir, 'testcases_nodeid_record.txt')
    with open(testcase_record_file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            testcase = {}
            testcase['node_id'] = line
            testcases.append(testcase)

    resp = requests.post(url=upload_server, json=testcases)
    print(resp.json())


if __name__ == '__main__':
    update_testcases()