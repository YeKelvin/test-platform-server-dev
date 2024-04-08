#!/usr/bin/ python3
# @File    : tpa_service.py
# @Time    : 2023-04-17 17:15:40
# @Author  : Kelvin.Ye
from app.modules.opencenter.dao import open_application_dao
from app.modules.opencenter.enum import AppState
from app.modules.opencenter.model import TOpenApplication
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_application_list(req):
    # 查询应用列表
    conds = QueryCondition()
    conds.like(TOpenApplication.APP_NO, req.appNo)
    conds.like(TOpenApplication.APP_NAME, req.appName)
    conds.like(TOpenApplication.APP_CODE, req.appCode)
    conds.like(TOpenApplication.APP_DESC, req.appDesc)
    conds.like(TOpenApplication.STATE, req.state)

    pagination = (
        TOpenApplication
        .filter(*conds)
        .order_by(TOpenApplication.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'appNo': tpa.APP_NO,
            'appName': tpa.APP_NAME,
            'appCode': tpa.APP_CODE,
            'appDesc': tpa.APP_DESC,
            'state': tpa.STATE
        }
        for tpa in pagination.items
    ]

    return {'list': data, 'total': pagination.total}


@http_service
def query_application_info(req):
    # 查询应用
    openapp = open_application_dao.select_by_no(req.appNo)
    check_exists(openapp, error='应用不存在')

    return {
        'appNo': openapp.APP_NO,
        'appName': openapp.APP_NAME,
        'appCode': openapp.APP_CODE,
        'appDesc': openapp.APP_DESC,
        'state': openapp.STATE
    }


@http_service
def create_application(req):
    # 唯一性校验
    if open_application_dao.select_by_name(req.appName):
        raise ServiceError(msg='应用名称已存在')
    if open_application_dao.select_by_code(req.appCode):
        raise ServiceError(msg='应用代码已存在')

    # 创建应用
    app_no = new_id()
    TOpenApplication.insert(
        APP_NO=app_no,
        APP_NAME=req.appName,
        APP_CODE=req.appCode,
        APP_DESC=req.appDesc,
        STATE=AppState.ENABLE.value
    )

    return {'appNo': app_no}


@http_service
def modify_application(req):
    # 查询应用
    openapp = open_application_dao.select_by_no(req.appNo)
    check_exists(openapp, error='应用不存在')

    # 唯一性校验
    if openapp.APP_NAME != req.appName and open_application_dao.select_by_name(req.appName):
        raise ServiceError(msg='应用名称已存在')
    if openapp.APP_CODE != req.appCode and open_application_dao.select_by_code(req.appCode):
        raise ServiceError(msg='应用代码已存在')

    # 更新应用信息
    openapp.update(
        APP_NAME=req.appName,
        APP_CODE=req.appCode,
        APP_DESC=req.appDesc
    )


@http_service
def modify_application_state(req):
    # 查询应用
    openapp = open_application_dao.select_by_no(req.appNo)
    check_exists(openapp, error='应用不存在')

    # 更新应用状态
    openapp.update(STATE=req.state)


@http_service
def remove_application(req):
    # 查询应用
    openapp = open_application_dao.select_by_no(req.appNo)
    check_exists(openapp, error='应用不存在')

    # 删除应用
    openapp.delete()
