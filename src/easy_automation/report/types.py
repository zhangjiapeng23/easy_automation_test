#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/8/10

from enum import Enum

UNIQUE_LABELS = ['severity', 'thread', 'host']


class Severity(str, Enum):
    BLOCKER = 'blocker'
    CRITICAL = 'critical'
    NORMAL = 'normal'
    TRIVIAL = 'trivial'


class LinkType:
    LINK = 'link'
    ISSUE = 'issue'
    TEST_CASE = 'tms'


class LabelType(str):
    EPIC = 'epic'
    FEATURE = 'feature'
    STORY = 'story'
    PARENT_SUITE = 'parentSuite'
    SUITE = 'suite'
    SUB_SUITE = 'subSuite'
    SEVERITY = 'severity'
    THREAD = 'thread'
    HOST = 'host'
    TAG = 'tag'
    ID = 'as_id'
    FRAMEWORK = 'framework'
    LANGUAGE = 'language'
    MANUAL = 'MANUAL'


class ParameterMode(Enum):
    HIDDEN = 'hidden'
    MASKED = 'masked'
    DEFAULT = None

