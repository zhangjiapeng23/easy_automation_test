#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/8/10
import threading
from collections import OrderedDict, defaultdict

from allure_commons._core import plugin_manager

from easy_automation.report.model import ExecutableItem, TestResult, Attachment
from easy_automation.utils.common import now


class ThreadContextItems:

    _thread_context = defaultdict(OrderedDict)
    _init_thread: threading.Thread

    @property
    def thread_context(self):
        context = self._thread_context[threading.current_thread()]
        if not context and threading.current_thread() is not self._init_thread:
            uuid, last_item = next(reversed(self._thread_context[self._init_thread].items()))
            context[uuid] = last_item
        return context

    def __init__(self, *args, **kwargs):
        self._init_thread = threading.current_thread()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        self._thread_context.__setitem__(key, value)

    def __getitem__(self, item):
        return self._thread_context.__getitem__(item)

    def __iter__(self):
        return self._thread_context.__iter__()

    def __reversed__(self):
        return self._thread_context.__reversed__()

    def get(self, key):
        return self._thread_context.get(key)

    def pop(self, key):
        return self._thread_context.pop(key)

    def cleanup(self):
        stop_threads = []
        for thread in self._thread_context.keys():
            if not thread.is_alive():
                stop_threads.append(thread)
        for thread in stop_threads:
            del self._thread_context[thread]


class EasyReporter:

    def __init__(self):
        self._items = ThreadContextItems()
        self._orphan_items = []

    def _update_item(self, uuid, **kwargs):
        item = self._items[uuid] if uuid else self._items[next(reversed(self._items))]
        for name, value in kwargs.items():
            attr = getattr(item, name)
            if isinstance(attr, list):
                attr.append(value)
            else:
                setattr(item, name, value)

    def _last_executable(self):
        for _uuid in reversed(self._items):
            if isinstance(self._items[_uuid], ExecutableItem):
                return _uuid

    def get_item(self, uuid):
        return self._items.get(uuid)

    def get_last_item(self, item_type=None):
        for _uuid in reversed(self._items):
            if item_type is None:
                return self._items.get(_uuid)
            if type(self._items[_uuid]) == item_type:
                return self._items.get(_uuid)

    def start_group(self, uuid, group):
        self._items[uuid] = group

    def stop_group(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)
        group = self._items.pop(uuid)
        plugin_manager.hook.report_container(container=group)

    def update_group(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)

    def start_before_fixture(self, parent_uuid, uuid, fixture):
        self._items.get(parent_uuid).befores.append(fixture)
        self._items[uuid] = fixture

    def stop_before_fixture(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)
        fixture = self._items.pop(uuid)
        fixture.stop = now()

    def start_after_fixture(self, parent_uuid, uuid, fixture):
        self._items.get(parent_uuid).afters.append(fixture)
        self._items[uuid] = fixture

    def stop_after_fixture(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)
        fixture = self._items.pop(uuid)
        fixture.stop = now()

    def schedule_test(self, uuid, test_case):
        self._items[uuid] = test_case

    def get_test(self, uuid):
        return self.get_item(uuid) if uuid else self.get_last_item(TestResult)

    def close_test(self, uuid):
        test_case = self._items.pop(uuid)
        self._items.cleanup()
        plugin_manager.hook.report_result(result=test_case)

    def drop_test(self, uuid):
        self._items.pop(uuid)

    def start_step(self, parent_uuid, uuid, step):
        parent_uuid = parent_uuid if parent_uuid else self._last_executable()
        if parent_uuid is None:
            self._orphan_items.append(uuid)
        else:
            self._items[parent_uuid].steps.append(step)
            self._items[uuid] = step

    def stop_step(self, uuid, **kwargs):
        if uuid in self._orphan_items:
            self._orphan_items.remove(uuid)
        else:
            self._update_item(uuid, **kwargs)
            self._items.pop(uuid)
