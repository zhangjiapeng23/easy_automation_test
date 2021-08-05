#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/3/15
import inspect
from functools import wraps

from appium.webdriver.common.mobileby import MobileBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import allure

from easy_automation.utils.custom_logging import Logs

log = Logs(__name__)

BLACK_LIST = []


def blacklist_collect(cls):

    members = inspect.getmembers(cls)
    for mem in members:
        if mem[0].startswith('__'):
            continue
        else:
            BLACK_LIST.append(mem[1])
    return cls


def blacklist_handler(func):

    @wraps(func)
    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (NoSuchElementException, TimeoutException) as exc:
            for element_selector in BLACK_LIST:
                element = self.driver.find_elements(*element_selector)
                if element:
                    element[0].click()
                    # use handle_blacklist decorator call func again,
                    # to deal with multiple blacklist display at same time.
                    decorator = blacklist_handler(func)
                    return decorator(self, *args, *kwargs)
            else:
                allure.attach(self.screenshot(), attachment_type=allure.attachment_type.PNG)
                log.error(f'Element find failed: {exc}')
                raise exc

    return wrap



