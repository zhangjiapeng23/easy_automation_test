#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/15
import json
import os

import requests

from .common import http_retry
from .setting import setting
from .exception import CommandError
from .custom_logging import Logs

log = Logs()


@http_retry(retry_times=3)
def update_result(build_url):
    try:
        WEB_PLATFORM_SERVER_HOST = setting.WEB_PLATFORM_SERVER_HOST
        WEB_PLATFORM_REPORT_UPLOAD_URL = setting.WEB_PLATFORM_REPORT_UPLOAD_URL
    except AttributeError:
        msg = 'WEB_SERVER_HOST or REPORT_UPLOAD_URL not set in settings'
        raise CommandError(msg)

    upload_url = WEB_PLATFORM_SERVER_HOST + WEB_PLATFORM_REPORT_UPLOAD_URL
    result_file = os.path.join(os.getcwd(), 'result_summary.json')
    with open(result_file, 'r', encoding='utf-8') as fp:
        result_data = json.load(fp)
    result_data['build_url'] = build_url
    result_data['allure_report_url'] = build_url + 'allure/'
    resp = requests.post(url=upload_url, json=result_data)
    log.info(resp.text)
    return resp

