#!/usr/bin python3
# @File    : org_controller.py
# @Time    : 2024-10-23 16:45:59
# @Author  : Kelvin.Ye
from app.modules.structure.dao import organization_dao
from app.modules.structure.model import TOrganization
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_org_list(req):
    # 查询组织列表
    conds = QueryCondition()
    conds.like(TOrganization.STATE, req.state)
    conds.like(TOrganization.ORG_NO, req.orgNo)
    conds.like(TOrganization.ORG_NAME, req.orgName)
    conds.like(TOrganization.ORG_DESC, req.orgDesc)

    pagination = (
        TOrganization
        .filter(*conds)
        .order_by(TOrganization.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'state': org.STATE,
            'orgNo': org.ORG_NO,
            'orgName': org.ORG_NAME,
            'orgDesc': org.ORG_DESC,
        }
        for org in pagination.items
    ]

    return {'list': data, 'total': pagination.total}


@http_service
def query_org_all():
    orgs = organization_dao.select_all()
    return [
        {
            'state': org.STATE,
            'orgNo': org.ORG_NO,
            'orgName': org.ORG_NAME,
            'orgDesc': org.ORG_DESC,
        }
        for org in orgs
    ]


@http_service
def query_org_info(req):
    # 查询组织
    org = organization_dao.select_by_no(req.orgNo)
    check_exists(org, error='组织不存在')

    return {
        'state': org.STATE,
        'orgNo': org.ORG_NO,
        'orgName': org.ORG_NAME,
        'orgDesc': org.ORG_DESC,
    }


@http_service
def create_org(req):
    # 唯一性校验
    if organization_dao.select_by_name(req.orgName):
        raise ServiceError(msg='组织名称已存在')

    # 创建组织
    org_no = new_id()
    TOrganization.insert(
        STATE='ENABLE',
        ORG_NO=org_no,
        ORG_NAME=req.orgName,
        ORG_DESC=req.orgDesc,
    )

    return {'orgNo': org_no}


@http_service
def modify_org(req):
    # 查询组织
    org = organization_dao.select_by_no(req.orgNo)
    check_exists(org, error='组织不存在')

    # 唯一性校验
    if org.ORG_NAME != req.orgName and organization_dao.select_by_name(req.orgName):
        raise ServiceError(msg='组织名称已存在')

    # 更新组织信息
    org.update(
        ORG_NAME=req.orgName,
        ORG_DESC=req.orgDesc,
    )


@http_service
def modify_org_state(req):
    # 查询组织
    org = organization_dao.select_by_no(req.orgNo)
    check_exists(org, error='组织不存在')

    # 更新组织状态
    org.update(STATE=req.state)


@http_service
def remove_org(req):
    # 查询组织
    org = organization_dao.select_by_no(req.orgNo)
    check_exists(org, error='组织不存在')

    # 查询组织空间列表
    # org_space_list = org_space_dao.select_all_by_orgno(req.orgNo)
    # TODO: 校验组织是否存在工作空间，有就自动解除绑定

    # 删除组织
    org.delete()
