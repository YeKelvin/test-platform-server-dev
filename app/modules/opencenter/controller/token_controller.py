#!/usr/bin python3
# @Module  : opencenter.controller
# @File    : token_controller.py
# @Time    : 2024-04-02 10:56:48
# @Author  : Kelvin.Ye
from app.modules.opencenter.controller import blueprint
from app.modules.opencenter.service import token_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/token/all')
@require_login
@require_permission
def query_token_all(CODE='QUERY_ACCESS_TOKEN'):
    """查询所有令牌"""
    req = JsonParser(
        Argument('owner', required=True, nullable=False, help='持有者编号不能为空')
    ).parse()
    return service.query_token_all(req)


@blueprint.get('/token')
@require_login
@require_permission
def query_token(CODE='QUERY_ACCESS_TOKEN'):
    """查询令牌信息"""
    req = JsonParser(
        Argument('tokenNo', required=True, nullable=False, help='令牌编号不能为空')
    ).parse()
    return service.query_token(req)


@blueprint.post('/app/token')
@require_login
@require_permission
def create_app_token(CODE='CREATE_ACCESS_TOKEN'):
    """根据应用创建令牌"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空'),
        Argument('tokenName', required=True, nullable=False, help='令牌名称不能为空'),
        Argument('tokenDesc'),
        Argument('expireTime'),
        Argument('permissions', type=list, required=True, nullable=False, help='权限列表不能为空'),
    ).parse()
    return service.create_app_token(req)


@blueprint.post('/user/token')
@require_login
@require_permission
def create_user_token(CODE='CREATE_ACCESS_TOKEN'):
    """根据用户创建令牌"""
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空'),
        Argument('tokenName', required=True, nullable=False, help='令牌名称不能为空'),
        Argument('tokenDesc'),
        Argument('expireTime'),
        Argument('permissions', type=list, required=True, nullable=False, help='权限列表不能为空'),
    ).parse()
    return service.create_user_token(req)


@blueprint.put('/token')
@require_login
@require_permission
def modify_token(CODE='MODIFY_ACCESS_TOKEN'):
    """修改令牌"""
    req = JsonParser(
        Argument('tokenNo', required=True, nullable=False, help='令牌编号不能为空'),
        Argument('tokenName', required=True, nullable=False, help='令牌名称不能为空'),
        Argument('tokenDesc'),
        Argument('permissions', type=list, required=True, nullable=False, help='权限列表不能为空'),
    ).parse()
    return service.modify_token(req)


@blueprint.delete('/token')
@require_login
@require_permission
def remove_token(CODE='REMOVE_ACCESS_TOKEN'):
    """修改令牌"""
    req = JsonParser(
        Argument('tokenNo', required=True, nullable=False, help='令牌编号不能为空')
    ).parse()
    return service.remove_token(req)
