#!/usr/bin python3
# @Module  : structure
# @File    : __init__.py
# @Time    : 2024-10-23 16:28:54
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('structure', __name__, url_prefix='/structure')


# from . import xxx_controller      # noqa
