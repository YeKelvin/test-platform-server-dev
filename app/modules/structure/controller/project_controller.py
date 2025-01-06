#!/usr/bin python3
# @File    : project_controller.py
# @Time    : 2024-10-23 16:46:36
# @Author  : Kelvin.Ye
from app.modules.structure.controller import blueprint
from app.modules.structure.service import project_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/project/list')
@require_login
@require_permission
def query_project_list(CODE='QUERY_PROJECT'):
    """分页查询项目列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('projectNo'),
        Argument('projectName'),
        Argument('projectDesc'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_project_list(req)


@blueprint.get('/project/all')
@require_login
@require_permission
def query_project_all(CODE='QUERY_PROJECT'):
    """查询全部项目"""
    req = JsonParser(
        Argument('workspaceNo')
    ).parse()
    return service.query_project_all(req)


@blueprint.get('/project/info')
@require_login
@require_permission
def query_project_info(CODE='QUERY_PROJECT'):
    """查询项目信息"""
    req = JsonParser(
        Argument('projectNo', required=True, nullable=False, help='项目编号不能为空')
    ).parse()
    return service.query_project_info(req)


@blueprint.post('/project')
@require_login
@require_permission
def create_project(CODE='CREATE_PROJECT'):
    """新增项目"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('projectName', required=True, nullable=False, help='项目名称不能为空'),
        Argument('projectDesc')
    ).parse()
    return service.create_project(req)


@blueprint.put('/project')
@require_login
@require_permission
def modify_project(CODE='MODIFY_PROJECT'):
    """更新项目信息"""
    req = JsonParser(
        Argument('projectNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('projectName', required=True, nullable=False, help='项目名称不能为空'),
        Argument('projectDesc'),
    ).parse()
    return service.modify_project(req)


@blueprint.put('/project/state')
@require_login
@require_permission
def modify_project_state(CODE='MODIFY_PROJECT'):
    """更新项目状态"""
    req = JsonParser(
        Argument('projectNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('state', required=True, nullable=False, help='项目状态不能为空')
    ).parse()
    return service.modify_project_state(req)


@blueprint.delete('/project')
@require_login
@require_permission
def remove_project(CODE='REMOVE_PROJECT'):
    """删除项目"""
    req = JsonParser(
        Argument('projectNo', required=True, nullable=False, help='项目编号不能为空')
    ).parse()
    return service.remove_project(req)
