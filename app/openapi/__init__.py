#!/usr/bin python3
# @Module  : openapi
# @File    : __init__.py
# @Time    : 2023-04-19 16:40:05
# @Author  : Kelvin.Ye
from flask import Blueprint


api = Blueprint('openapi', __name__, url_prefix='/openapi')


# 加载子路由
from .testing.controller import blueprint as testing_blueprint    # noqa


# 注册子路由
api.register_blueprint(testing_blueprint)
