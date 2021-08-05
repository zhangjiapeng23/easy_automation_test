#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/8/5
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from easy_automation.utils.custom_logging import Logs

log = Logs(__name__)


class AppiumMixin:
    EXPLICIT_WAIT = 8

    # def __init__(self, driver: WebDriver):
    #     self.driver = driver

    def find(self, element_selector, timeout=EXPLICIT_WAIT):
        log.info(f'Find element {element_selector[1]}')
        return WebDriverWait(self.driver, timeout)\
            .until(EC.presence_of_element_located(element_selector))

    def finds(self, element_selector, timeout=EXPLICIT_WAIT):
        log.info(f'Find elements {element_selector[1]}')
        return WebDriverWait(self.driver, timeout=timeout)\
            .until(EC.presence_of_all_elements_located(element_selector))

    def click_element(self, element_selector, timeout=EXPLICIT_WAIT):
        element = WebDriverWait(self.driver, timeout=timeout) \
            .until(EC.element_to_be_clickable(element_selector))
        element.click()

    def click_elements(self, element_selector, timeout=EXPLICIT_WAIT, _slice=None):
        """
        :param element_seletctor:
        :param timeout:
        :param _slice
        :return:
        """
        log.info('click elements {1} by {0}'.format(*element_selector))
        elements = self._clickable_elements(element_selector, timeout)
        if _slice and isinstance(_slice, slice):
            elements = elements[_slice]
        for element in elements:
            element.click()

    def send_value(self, element_selector, value, timeout=EXPLICIT_WAIT):
        self.find(element_selector, timeout).send_keys(value)

    def scroll_up_find(self, element_selector, timeout=EXPLICIT_WAIT, max_time=5):
        while max_time:
            element = self.finds(element_selector, timeout)
            if element:
                return element[0]
            else:
                screen_size = self.driver.get_window_size()
                width = screen_size['width']
                height = screen_size['height']
                self.driver.swipe(width * 0.5, height * 0.75, width * 0.5, height * 0.25)
                max_time -= 1
        raise NoSuchElementException(element_selector)

    def screenshot(self):
        log.info('Get screenshot.')
        return self.driver.get_screenshot_as_png()

    def _clickable_elements(self, element_selector, timeout=EXPLICIT_WAIT):
        """
        :param element_seletctor:
        :param timeout:
        :return:
        """
        elements = WebDriverWait(self.driver, timeout=timeout)\
            .until(elements_to_be_clickable(element_selector))
        return elements


class elements_to_be_clickable(object):
    """ An Expectation for checking al elements is visible and enabled such that
    you can click they."""
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        elements = EC.visibility_of_all_elements_located(self.locator)(driver)
        clickable_elements = []
        if elements:
            for element in elements:
                if element.is_enabled():
                    clickable_elements.append(element)
                else:
                    return False
            return clickable_elements
        else:
            return False