#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2024/8/30
from flask import Blueprint

bp = Blueprint('health', __name__)


@bp.get("/health")
def health_check():
    return "ok"

