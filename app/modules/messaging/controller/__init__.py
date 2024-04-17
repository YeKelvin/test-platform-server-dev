#!/usr/bin python3
# @Module  : messaging
# @File    : __init__.py
# @Time    : 2024-04-17 11:40:06
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('messaging', __name__, url_prefix='/messaging')


from . import log_controller        # noqa
from . import notice_controller     # noqa
