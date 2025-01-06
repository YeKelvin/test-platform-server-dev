#!/usr/bin python3
# @File    : module_controller.py
# @Time    : 2024-10-23 16:47:29
# @Author  : Kelvin.Ye
from app.modules.structure.controller import blueprint
from app.modules.structure.service import module_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/module/list')
@require_login
@require_permission
def query_module_list(CODE='QUERY_MODULE'):
    """分页查询模块列表"""
    req = JsonParser(
        Argument('moduleNo'),
        Argument('moduleName'),
        Argument('moduleDesc'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_module_list(req)


@blueprint.get('/module/all')
@require_login
@require_permission
def query_module_all(CODE='QUERY_MODULE'):
    """查询全部模块"""
    return service.query_module_all()


@blueprint.get('/module/info')
@require_login
@require_permission
def query_module_info(CODE='QUERY_MODULE'):
    """查询模块信息"""
    req = JsonParser(
        Argument('moduleNo', required=True, nullable=False, help='模块编号不能为空')
    ).parse()
    return service.query_module_info(req)


@blueprint.post('/module')
@require_login
@require_permission
def create_module(CODE='CREATE_MODULE'):
    """新增模块"""
    req = JsonParser(
        Argument('moduleName', required=True, nullable=False, help='模块名称不能为空'),
        Argument('moduleDesc')
    ).parse()
    return service.create_module(req)


@blueprint.put('/module')
@require_login
@require_permission
def modify_module(CODE='MODIFY_MODULE'):
    """更新模块信息"""
    req = JsonParser(
        Argument('moduleNo', required=True, nullable=False, help='模块编号不能为空'),
        Argument('moduleName', required=True, nullable=False, help='模块名称不能为空'),
        Argument('moduleDesc'),
    ).parse()
    return service.modify_module(req)


@blueprint.put('/module/state')
@require_login
@require_permission
def modify_module_state(CODE='MODIFY_MODULE'):
    """更新模块状态"""
    req = JsonParser(
        Argument('moduleNo', required=True, nullable=False, help='模块编号不能为空'),
        Argument('state', required=True, nullable=False, help='模块状态不能为空')
    ).parse()
    return service.modify_module_state(req)


@blueprint.delete('/module')
@require_login
@require_permission
def remove_module(CODE='REMOVE_MODULE'):
    """删除模块"""
    req = JsonParser(
        Argument('moduleNo', required=True, nullable=False, help='模块编号不能为空')
    ).parse()
    return service.remove_module(req)
