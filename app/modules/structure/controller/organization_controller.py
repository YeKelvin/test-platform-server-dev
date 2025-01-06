#!/usr/bin python3
# @File    : org_controller.py
# @Time    : 2024-10-23 16:45:59
# @Author  : Kelvin.Ye
from app.modules.structure.controller import blueprint
from app.modules.structure.service import organization_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/org/list')
@require_login
@require_permission
def query_org_list(CODE='QUERY_ORG'):
    """分页查询组织列表"""
    req = JsonParser(
        Argument('orgNo'),
        Argument('orgName'),
        Argument('orgDesc'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_org_list(req)


@blueprint.get('/org/all')
@require_login
@require_permission
def query_org_all(CODE='QUERY_ORG'):
    """查询全部组织"""
    return service.query_org_all()


@blueprint.get('/org/info')
@require_login
@require_permission
def query_org_info(CODE='QUERY_ORG'):
    """查询组织信息"""
    req = JsonParser(
        Argument('orgNo', required=True, nullable=False, help='组织编号不能为空')
    ).parse()
    return service.query_org_info(req)


@blueprint.post('/org')
@require_login
@require_permission
def create_org(CODE='CREATE_ORG'):
    """新增组织"""
    req = JsonParser(
        Argument('orgName', required=True, nullable=False, help='组织名称不能为空'),
        Argument('orgDesc')
    ).parse()
    return service.create_org(req)


@blueprint.put('/org')
@require_login
@require_permission
def modify_org(CODE='MODIFY_ORG'):
    """更新组织信息"""
    req = JsonParser(
        Argument('orgNo', required=True, nullable=False, help='组织编号不能为空'),
        Argument('orgName', required=True, nullable=False, help='组织名称不能为空'),
        Argument('orgDesc'),
    ).parse()
    return service.modify_org(req)


@blueprint.put('/org/state')
@require_login
@require_permission
def modify_org_state(CODE='MODIFY_ORG'):
    """更新组织状态"""
    req = JsonParser(
        Argument('orgNo', required=True, nullable=False, help='组织编号不能为空'),
        Argument('state', required=True, nullable=False, help='组织状态不能为空')
    ).parse()
    return service.modify_org_state(req)


@blueprint.delete('/org')
@require_login
@require_permission
def remove_org(CODE='REMOVE_ORG'):
    """删除组织"""
    req = JsonParser(
        Argument('orgNo', required=True, nullable=False, help='组织编号不能为空')
    ).parse()
    return service.remove_org(req)
