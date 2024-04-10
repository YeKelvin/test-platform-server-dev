#!/usr/bin/ python3
# @File    : workspace_controller.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from app.modules.public.controller import blueprint
from app.modules.public.service import workspace_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/workspace/list')
@require_login
@require_permission
def query_workspace_list(CODE='QUERY_WORKSPACE'):
    """分页查询工作空间列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('workspaceName'),
        Argument('workspaceDesc'),
        Argument('workspaceScope'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_workspace_list(req)


@blueprint.get('/workspace/all')
@require_login
@require_permission
def query_workspace_all(CODE='QUERY_WORKSPACE'):
    """查询全部工作空间"""
    req = JsonParser(
        Argument('userNo'),
        Argument('scopes', type=list)
    ).parse()
    return service.query_workspace_all(req)


@blueprint.get('/workspace/info')
@require_login
@require_permission
def query_workspace_info(CODE='QUERY_WORKSPACE'):
    """查询工作空间信息"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空')
    ).parse()
    return service.query_workspace_info(req)


@blueprint.post('/workspace')
@require_login
@require_permission
def create_workspace(CODE='CREATE_WORKSPACE'):
    """新增工作空间"""
    req = JsonParser(
        Argument('workspaceName', required=True, nullable=False, help='工作空间名称不能为空'),
        Argument('workspaceDesc'),
        Argument('workspaceScope', required=True, nullable=False, help='工作空间作用域不能为空')
    ).parse()
    return service.create_workspace(req)


@blueprint.put('/workspace')
@require_login
@require_permission
def modify_workspace(CODE='MODIFY_WORKSPACE'):
    """修改工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空'),
        Argument('workspaceName', required=True, nullable=False, help='工作空间名称不能为空'),
        Argument('workspaceDesc'),
        Argument('workspaceScope', required=True, nullable=False, help='工作空间作用域不能为空')
    ).parse()
    return service.modify_workspace(req)


@blueprint.delete('/workspace')
@require_login
@require_permission
def remove_workspace(CODE='REMOVE_WORKSPACE'):
    """删除工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空'),
    ).parse()
    return service.remove_workspace(req)
