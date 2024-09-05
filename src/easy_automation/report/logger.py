#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/9/11

from allure_commons import hookimpl
from attr import asdict


class MemoryLogger:

    def __init__(self):
        self.test_cases = []
        self.test_containers = []
        self.attachments = {}

    @hookimpl
    def report_result(self, result):
        data = asdict(result, filter=lambda _, v: v or v is False)
        self.test_cases.append(data)

    @hookimpl
    def report_container(self, container):
        data = asdict(container, filter=lambda _, v: v or v is False)
        self.test_containers.append(data)

    @hookimpl
    def report_attached_file(self, source, file_name):
        self.attachments[file_name] = source

    @hookimpl
    def report_attached_data(self, body, file_name):
        self.attachments[file_name] = body

    def clear_data(self):
        self.test_cases = []
        self.test_containers = []
        self.attachments = {}