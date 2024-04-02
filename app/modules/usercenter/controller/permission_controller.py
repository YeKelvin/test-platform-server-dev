#!/usr/bin/ python3
# @File    : permission_controller.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.modules.usercenter.controller import blueprint
from app.modules.usercenter.service import permission_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/permission/all')
@require_login
@require_permission
def query_permission_all(CODE='QUERY_PERMISSION'):
    """查询全部权限"""
    req = JsonParser(
        Argument('moduleCodes', type=list),
        Argument('objectCodes', type=list),
        Argument('actExcludes', type=list),
    ).parse()
    return service.query_permission_all(req)


@blueprint.get('/open/permission/all')
@require_login
@require_permission
def query_open_permission_all(CODE='QUERY_PERMISSION'):
    """查询全部开放接口的权限"""
    return service.query_open_permission_all()
