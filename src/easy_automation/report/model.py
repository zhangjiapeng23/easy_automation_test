#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/8/9

from attr import attrs, attrib
from attr import Factory

ATTACHMENT_PATTERN = '{prefix}-attachment.{ext}'


@attrs
class TestResultContainer:
    uuid = attrib(default=None)
    name = attrib(default=None)
    children = attrib(default=Factory(list))
    description = attrib(default=None)
    descriptionHtml = attrib(default=None)
    befores = attrib(default=Factory(list))
    afters = attrib(default=Factory(list))
    links = attrib(default=Factory(list))
    start = attrib(default=None)
    stop = attrib(default=None)


@attrs
class ExecutableItem:
    name = attrib(default=None)
    status = attrib(default=None)
    statusDetails = attrib(default=None)
    stage = attrib(default=None)
    description = attrib(default=None)
    descriptionHtml = attrib(default=None)
    steps = attrib(default=Factory(list))
    attachments = attrib(default=Factory(list))
    parameters = attrib(default=Factory(list))
    start = attrib(default=None)
    stop = attrib(default=None)


@attrs
class TestResult(ExecutableItem):
    uuid = attrib(default=None)
    historyId = attrib(default=None)
    testCaseId = attrib(default=None)
    fullName = attrib(default=None)
    labels = attrib(default=Factory(list))
    links = attrib(default=Factory(list))


@attrs
class TestStepResult(ExecutableItem):
    id = attrib(default=None)


@attrs
class TestBeforeResult(ExecutableItem):
    pass


@attrs
class TestAfterResult(ExecutableItem):
    pass


@attrs
class Parameter:
    name = attrib(default=None)
    value = attrib(default=None)
    excluded = attrib(default=None)
    mode = attrib(default=None)


@attrs
class Label:
    name = attrib(default=None)
    value = attrib(default=None)


@attrs
class Link:
    type = attrib(default=None)
    url = attrib(default=None)
    name = attrib(default=None)


@attrs
class StatusDetails:
    known = attrib(default=None)
    flaky = attrib(default=None)
    message = attrib(default=None)
    trace = attrib(default=None)


@attrs
class Attachment:
    name = attrib(default=None)
    source = attrib(default=None)
    type = attrib(default=None)


class Status:
    FAILED = 'failed'
    BROKEN = 'broken'
    PASSED = 'passed'
    SKIPPED = 'skipped'
    UNKNOWN = 'unknown'

