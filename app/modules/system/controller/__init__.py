#!/usr/bin/ python3
# @File    : __init__.py
# @Time    : 2021/6/2 00:08
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('system', __name__, url_prefix='/system')


from . import apilog_controller                 # noqa
from . import data_controller                   # noqa
from . import platform_controller               # noqa
from . import tag_controller                    # noqa
from . import workspace_controller              # noqa
from . import workspace_member_controller       # noqa
from . import workspace_restriction_controller  # noqa
