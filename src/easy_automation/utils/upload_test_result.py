#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/15
import json
import sys
import time
from functools import wraps
import os

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from setting import WEB_SERVER_HOST, REPORT_UPLOAD_URL

root_dir = os.path.join(os.path.dirname(__file__), '..')


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


@http_retry(retry_times=3)
def update_result(build_url):
    upload_url = WEB_SERVER_HOST + REPORT_UPLOAD_URL
    result_file = os.path.join(root_dir, 'result_summary.json')
    with open(result_file, 'r', encoding='utf-8') as fp:
        result_data = json.load(fp)
    result_data['build_url'] = build_url
    result_data['allure_report_url'] = build_url + 'allure/'
    resp = requests.post(url=upload_url, json=result_data)
    print(resp.text)
    return resp


if __name__ == '__main__':
    params = sys.argv
    if len(params) <= 1:
        print('miss build_url param.')
    else:
        build_url = sys.argv[1]
        update_result(build_url)
