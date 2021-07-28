#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/27

from selenium.webdriver.common.by import By


class Xpath:

    def __init__(self, element_location):
        self._element_location = element_location

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.XPATH, self._element_location


class Id:

    def __init__(self, element_location):
        self._element_location = element_location

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.ID, self._element_location


class LinkText:

    def __init__(self, element_location):
        self._element_location = element_location

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.LINK_TEXT, self._element_location


class PartialLinkText:

    def __init__(self, element_location):
        self._element_location = element_location

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.PARTIAL_LINK_TEXT, self._element_location


class Name:

    def __init__(self, element_location):
        self._element_location = element_location

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.NAME, self._element_location


class TagName:

    def __init__(self, element_location):
        self._element_location = element_location

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.LINK_TEXT, self._element_location

class ClassName:

    def __init__(self, element_location):
        self._element_location = element_location

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.CLASS_NAME, self._element_location


class CssSelector:

    def __init__(self, element_location):
        self._element_location = element_location

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.CSS_SELECTOR, self._element_location

