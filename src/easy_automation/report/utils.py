#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/8/30

import traceback
from traceback import format_exception_only
import string

import pytest
import platform

from easy_automation.report.model import Status, StatusDetails
from easy_automation.utils.common import md5
from easy_automation.report.types import LabelType


EASY_DESCRIPTION_MARK = 'easy_description'
EASY_DESCRIPTION_HTML_MARK = 'east_description_html'
EASY_LABEL_MARK = 'easy_label'
EASY_LINK_MARk = 'easy_link'

EASY_UNIQUE_LABELS = [
    LabelType.SEVERITY,
    LabelType.FRAMEWORK,
    LabelType.HOST,
    LabelType.SUITE,
    LabelType.PARENT_SUITE,
    LabelType.SUB_SUITE
]


class SafeFormatter(string.Formatter):
    """
    Format string safely - skip any non-passed keys
    >>> f = SafeFormatter().format

    Make sure we don't broke default formatting behaviour
    >>> f("literal string")
    'literal string'
    >>> f("{expected.format}", expected=str)
    "<method 'format' of 'str' objects>"
    >>> f("{expected[0]}", expected=["value"])
    'value'
    >>> f("{expected[0]}", expected=123)
    Traceback (most recent call last):
    ...
    TypeError: 'int' object is not subscriptable
    >>> f("{expected[0]}", expected=[])
    Traceback (most recent call last):
    ...
    IndexError: list index out of range
    >>> f("{expected.format}", expected=int)
    Traceback (most recent call last):
    ...
    AttributeError: type object 'int' has no attribute 'format'

    Check that unexpected keys do not cause some errors
    >>> f("{expected} {unexpected}", expected="value")
    'value {unexpected}'
    >>> f("{unexpected[0]}", expected=["value"])
    '{unexpected[0]}'
    >>> f("{unexpected.format}", expected=str)
    '{unexpected.format}'
    """

    class SafeKeyOrIndexError(Exception):
        pass

    def get_field(self, field_name, args, kwargs):
        try:
            return super().get_field(field_name, args, kwargs)
        except self.SafeKeyOrIndexError:
            return "{" + field_name + "}", field_name

    def get_value(self, key, args, kwargs):
        try:
            return super().get_value(key, args, kwargs)
        except (KeyError, IndexError):
            raise self.SafeKeyOrIndexError()


def represent(item):
    """
    >>> represent(None)
    'None'

    >>> represent(123)
    '123'

    >>> represent('hi')
    "'hi'"

    >>> represent('привет')
    "'привет'"

    >>> represent(bytearray([0xd0, 0xbf]))  # doctest: +ELLIPSIS
    "<... 'bytearray'>"

    >>> from struct import pack
    >>> represent(pack('h', 0x89))
    "<class 'bytes'>"

    >>> represent(int)
    "<class 'int'>"

    >>> represent(represent)  # doctest: +ELLIPSIS
    '<function represent at ...>'

    >>> represent([represent])  # doctest: +ELLIPSIS
    '[<function represent at ...>]'

    >>> class ClassWithName:
    ...     pass

    >>> represent(ClassWithName)
    "<class 'utils.ClassWithName'>"
    """

    if isinstance(item, str):
        return f"'{item}'"
    elif isinstance(item, (bytes, bytearray)):
        return repr(type(item))
    else:
        return repr(item)


def get_status(exception):
    if exception:
        if isinstance(exception, AssertionError) or isinstance(exception, pytest.fail.Exception):
            return Status.FAILED
        elif isinstance(exception, pytest.skip.Exception):
            return Status.SKIPPED
        return Status.BROKEN
    else:
        return Status.PASSED


def get_status_details(exception_type, exception, exception_traceback):
    message = format_exception(exception_type, exception)
    trace = format_traceback(exception_traceback)
    return StatusDetails(message=message, trace=trace) if message or trace else None


def format_traceback(exc_traceback):
    return ''.join(traceback.format_tb(exc_traceback)) if exc_traceback else None


def format_exception(etype, value):
    return '\n'.join(format_exception_only(etype, value)) if etype or value else None


def get_marker_value(item, keyword):
    marker = item.get_closest_marker(keyword)
    return marker.args[0] if marker and marker.args else None


def easy_description(item):
    description = get_marker_value(item, EASY_DESCRIPTION_MARK)
    if description:
        return description
    elif hasattr(item, 'function'):
        return item.function.__doc__


def easy_description_html(item):
    return get_marker_value(item, EASY_DESCRIPTION_HTML_MARK)


def easy_title(item):
    return getattr(
        getattr(item, "obj", None),
        "__allure_display_name__",
        None
    )


def easy_package(item):
    parts = item.nodeid.split("::")
    path = parts[0].rsplit(".", 1)[0]
    return path.replace('/', '.')


def easy_name(item, parameters):
    name = item.name
    title = easy_title(item)
    return SafeFormatter().format(
        title,
        **{**parameters, **item.funcargs}
    ) if title else name


def easy_label(item, label):
    labels = []
    for mark in item.iter_markers(name=EASY_LABEL_MARK):
        if mark.kwargs.get("label_type") == label:
            labels.extend(mark.args)
    return labels


def easy_labels(item):
    unique_labels = dict()
    labels = set()
    for mark in item.iter_markers(name=EASY_LABEL_MARK):
        label_type = mark.kwargs["label_type"]
        if label_type in EASY_UNIQUE_LABELS:
            if label_type not in unique_labels.keys():
                unique_labels[label_type] = mark.args[0]
        else:
            for arg in mark.args:
                labels.add((label_type, arg))
    for k, v in unique_labels.items():
        labels.add((k, v))
    return labels


def easy_full_name(item: pytest.Item):
    pacakge = easy_package(item)
    class_name = f".{item.parent.name}" if isinstance(item.parent, pytest.Class) else ''
    test = item.originalname if isinstance(item, pytest.Function) else item.name.split("[")[0]
    full_name = f"{pacakge}{class_name}#{test}"
    return full_name


def get_history_id(full_name, parameters, original_values):
    return md5(full_name,
               *(original_values.get(p.name, p.value) for p in sorted(
                   filter(
                       lambda p: not p.excluded,
                       parameters
                   ),
                   key=lambda p: p.name
               )))

def pytest_markers(item):
    for keyword in item.keywords.keys():
        if any([keyword.startswith('allure_'), keyword == 'parametrize']):
            continue
        marker = item.get_closest_marker(keyword)
        if marker is None:
            continue

        yield mark_to_str(marker)


def mark_to_str(marker):
    args = [represent(arg) for arg in marker.args]
    kwargs = [f'{key}={represent(value)}' for key, value in marker.kwargs.items()]
    if marker.name in ('filterwarnings', 'skip', 'skipif', 'xfail', 'usefixtures', 'tryfirst', 'trylast'):
        markstr = f'@pytest.mark.{marker.name}'
    else:
        markstr = str(marker.name)
    if args or kwargs:
        parameters = ', '.join(args + kwargs)
        markstr = f'{markstr}({parameters})'
    return markstr


def platform_label():
    major_version, *_ = platform.python_version_tuple()
    implementation = platform.python_implementation().lower()
    return f'{implementation}{major_version}'


def easy_package(item):
    parts = item.nodeid.split('::')
    path = parts[0].rsplit('.', 1)[0]
    return path.replace('/', '.')


def easy_links(item):
    for mark in item.iter_markers(name=EASY_LINK_MARk):
        yield (mark.kwargs['link_type'], mark.args[0], mark.kwargs['name'])


def get_outcome_status(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    return get_status(exception)


def get_outcome_status_details(outcome):
    exception_type, exception, exception_traceback = outcome.excinfo or (None, None, None)
    return get_status_details(exception_type, exception, exception_traceback)


def get_pytest_report_status(pytest_report):
    pytest_statuses = ('failed', 'passed', 'skipped')
    statuses = (Status.FAILED, Status.PASSED, Status.SKIPPED)
    for pytest_status, status in zip(pytest_statuses, statuses):
        if getattr(pytest_report, pytest_status):
            return status


def format_easy_link(config, url, link_type):
    pattern = dict(config.option.allure_link_pattern).get(link_type, '{}')
    return pattern.format(url)