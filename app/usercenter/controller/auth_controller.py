#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : auth_controller.py
# @Time    : 2020/6/12 18:24
# @Author  : Kelvin.Ye
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.usercenter.controller import blueprint
from app.usercenter.service import auth_service as service


log = get_logger(__name__)


@blueprint.get('/encryption/factor')
def create_rsa_public_key():
    """获取加密因子"""
    req = JsonParser(
        Argument('loginName', required=True, nullable=False, help='登录账号不能为空')
    ).parse()
    return service.create_rsa_public_key(req)
