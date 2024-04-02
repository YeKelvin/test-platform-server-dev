#!/usr/bin/env python
# @File    : application_controller.py
# @Time    : 2023-04-17 17:14:51
# @Author  : Kelvin.Ye
from app.modules.opencenter.controller import blueprint
from app.modules.opencenter.enum import AppState
from app.modules.opencenter.service import application_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/application/list')
@require_login
@require_permission
def query_application_list(CODE='QUERY_APPLICATION'):
    """分页查询应用列表"""
    req = JsonParser(
        Argument('appNo'),
        Argument('appName'),
        Argument('appCode'),
        Argument('appDesc'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_application_list(req)


@blueprint.get('/application/info')
@require_login
@require_permission
def query_application_info(CODE='QUERY_APPLICATION'):
    """查询应用信息"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空')
    ).parse()
    return service.query_application_info(req)


@blueprint.post('/application')
@require_login
@require_permission
def create_application(CODE='CREATE_APPLICATION'):
    """新增第三方应用"""
    req = JsonParser(
        Argument('appName', required=True, nullable=False, help='应用名称不能为空'),
        Argument('appCode'),
        Argument('appDesc')
    ).parse()
    return service.create_application(req)


@blueprint.put('/application')
@require_login
@require_permission
def modify_application(CODE='MODIFY_APPLICATION'):
    """更新应用信息"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空'),
        Argument('appName', required=True, nullable=False, help='应用名称不能为空'),
        Argument('appCode'),
        Argument('appDesc')
    ).parse()
    return service.modify_application(req)


@blueprint.put('/application/state')
@require_login
@require_permission
def modify_application_state(CODE='MODIFY_APPLICATION'):
    """更新应用状态"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空'),
        Argument('state', required=True, nullable=False, enum=AppState, help='应用状态不能为空')
    ).parse()
    return service.modify_application_state(req)


@blueprint.delete('/application')
@require_login
@require_permission
def remove_application(CODE='REMOVE_APPLICATION'):
    """删除应用"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空')
    ).parse()
    return service.remove_application(req)
