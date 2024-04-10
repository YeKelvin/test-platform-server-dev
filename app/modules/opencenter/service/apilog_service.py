#!/usr/bin python3
# @File    : apilog_service.py
# @Time    : 2023-04-21 09:07:58
# @Author  : Kelvin.Ye
from sqlalchemy import or_

from app.database import db_query
from app.modules.opencenter.model import TOpenApiLog
from app.modules.opencenter.model import TOpenApplication
from app.modules.usercenter.model import TUser
from app.tools.service import http_service
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import TIMEFMT


@http_service
def query_openapi_log_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.add(or_(TUser.USER_NAME.like(f'%{req.invokeBy}%'), TOpenApplication.APP_NAME.like(f'%{req.invokeBy}%')))
    conds.like(TOpenApiLog.METHOD, req.method)
    conds.like(TOpenApiLog.URI, req.path)
    conds.like(TOpenApiLog.REQUEST, req.request)
    conds.like(TOpenApiLog.RESPONSE, req.response)
    conds.equal(TOpenApiLog.SUCCESS, req.success)
    conds.ge(TOpenApiLog.CREATED_TIME, req.startTime)
    conds.le(TOpenApiLog.CREATED_TIME, req.endTime)

    # 查询日志列表
    pagination = (
        db_query(
            TUser.USER_NAME,
            TOpenApplication.APP_NAME,
            TOpenApiLog.LOG_NO,
            TOpenApiLog.APP_NO,
            TOpenApiLog.USER_NO,
            TOpenApiLog.DESC,
            TOpenApiLog.IP,
            TOpenApiLog.METHOD,
            TOpenApiLog.URI,
            TOpenApiLog.REQUEST,
            TOpenApiLog.RESPONSE,
            TOpenApiLog.SUCCESS,
            TOpenApiLog.ELAPSED_TIME,
            TOpenApiLog.CREATED_TIME
        )
        .outerjoin(TUser, TUser.USER_NO == TOpenApiLog.USER_NO)
        .outerjoin(TOpenApplication, TOpenApplication.APP_NO == TOpenApiLog.APP_NO)
        .filter(*conds)
        .order_by(TOpenApiLog.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'logNo': entity.LOG_NO,
            'method': entity.METHOD,
            'path': entity.URI,
            'desc': entity.DESC,
            'request': entity.REQUEST,
            'response': entity.RESPONSE,
            'success': entity.SUCCESS,
            'elapsedTime': entity.ELAPSED_TIME,
            'invokeBy': entity.APP_NAME or entity.USER_NAME,
            'invokeIp': entity.IP,
            'invokeTime': entity.CREATED_TIME.strftime(TIMEFMT)
        }
        for entity in pagination.items
    ]

    return {'list': data, 'total': pagination.total}
