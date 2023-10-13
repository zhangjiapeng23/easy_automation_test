#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/8/30
import allure_commons
import pytest

from easy_automation.utils.common import uuid4, host_tag, thread_tag, now, md5
from easy_automation.report.types import LabelType
from easy_automation.report.reporter import EasyReporter
from easy_automation.report.model import *
from easy_automation.report.utils import get_status, get_status_details, easy_name, easy_full_name, easy_description, \
    easy_description_html, represent,get_history_id


class EasyListener:

    SUITE_LABELS = {
        LabelType.PARENT_SUITE,
        LabelType.SUITE,
        LabelType.SUB_SUITE
    }

    def __init__(self, config):
        self.config = config
        self.easy_logger = EasyReporter()
        self._cache = ItemCache()
        self._host = host_tag()
        self._thread = thread_tag()

    @allure_commons.hookimpl
    def start_step(self, uuid, title, params):
        parameters = [Parameter(name=name, value=value) for name, value in params.items()]
        step = TestStepResult(name=title, start=now(), parameters=parameters)
        self.easy_logger.start_step(None, uuid, step)

    @allure_commons.hookimpl
    def stop_step(self, uuid, exc_type, exc_val, exc_tb):
        self.easy_logger.stop_step(uuid,
                                   stop=now(),
                                   status=get_status(exc_val),
                                   statusDetails=get_status_details(exc_type, exc_val, exc_tb))

    @allure_commons.hookimpl
    def start_fixture(self, parent_uuid, uuid, name):
        after_fixture = TestAfterResult(name=name, start=now())
        self.easy_logger.start_after_fixture(parent_uuid, uuid, after_fixture)

    @allure_commons.hookimpl
    def stop_fixture(self, parent_uuid, uuid, name, exc_type, exc_val, exc_tb):
        self.easy_logger.stop_after_fixture(uuid,
                                            stop=now(),
                                            status=get_status(exc_val),
                                            statusDetails=get_status_details(exc_type, exc_val, exc_tb))

    def _update_fixtures_children(self, item):
        uuid = self._cache.get(item.nodeid)
        for fixturedef in _test_fixtures(item):
            group_uuid = self._cache.get(fixturedef)
            if group_uuid:
                group = self.easy_logger.get_item(group_uuid)
            else:
                group_uuid = self._cache.push(fixturedef)
                group = TestResultContainer(uuid=group_uuid)
                self.easy_logger.start_group(group_uuid, group)
            if uuid not in group.children:
                self.easy_logger.update_group(group_uuid, children=uuid)

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item, nextitem):
        uuid = self._cache.push(item.nodeid)
        test_result = TestResult(name=item.name, uuid=uuid, start=now(), stop=now())
        self.easy_logger.schedule_test(uuid, test_result)
        yield
        uuid = self._cache.pop(item.nodeid)
        if uuid:
            test_result = self.easy_logger.get_test(uuid)
            if test_result.status is None:
                test_result.status = Status.SKIPPED
            self.easy_logger.close_test(uuid)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self, item):
        if not self._cache.get(item.nodeid):
            uuid = self._cache.push(item.nodeid)
            test_result = TestResult(name=item.name, uuid=uuid, start=now(), stop=now())
            self.easy_logger.schedule_test(uuid, test_result)
        yield
        self._update_fixtures_children(item)
        uuid = self._cache.get(item.nodeid)
        test_result = self.easy_logger.get_test(uuid)
        params = self.__get_ptytest_params(item)
        test_result.name = easy_name(item, params)
        full_name = easy_full_name(item)
        test_result.full_name = full_name
        test_result.testCaseId = md5(full_name)
        test_result.description = easy_description(item)
        test_result.descriptionHtml = easy_description_html(item)
        current_param_names = [param.name for param in test_result.parameters]
        test_result.parametes.extend([
            Parameter(name=name, value=represent(value)) for name, value in params.items
            if name not in current_param_names
        ])

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        uuid = self._cache.get(item.nodeid)
        test_result = self.easy_logger.get_test(uuid)
        if test_result:
            self.easy_logger.drop_test(uuid)
            self.easy_logger.schedule_test(uuid, test_result)
            test_result.start = now()
        yield
        self._update_fixtures_children(item)
        if test_result:
            test_result.stop = now()

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(self, item):
        yield
        uuid = self._cache.get(item.nodeid)
        test_result = self.easy_logger.get_test(uuid)
        test_result.historyId = get_history_id(
            test_result.fullName,
            test_result.parameters,
            original_values=self.__get_pytest_params(item)
        )
        test_result.labels.extend([Label(name=name, value=value) for name, value in easy_labels(item)])

class ItemCache:

    def __init__(self):
        self._items = {}

    def get(self, _id):
        return self._items.get(id(_id))

    def push(self, _id):
        return self._items.setdefault(id(_id), uuid4())

    def pop(self, _id):
        return self._items.pop(id(_id), None)


def _test_fixtures(item):
    fixturemanager = item.session._fixturemanager
    fixturedefs = []

    if hasattr(item, "_request") and hasattr(item._request, "fixturenames"):
        for name in item._request.fixturenames:
            fixturedefs_pytest = fixturemanager.getfixturedefs(name, item.nodeid)
            if fixturedefs_pytest:
                fixturedefs.extend(fixturedefs_pytest)
    return fixturedefs