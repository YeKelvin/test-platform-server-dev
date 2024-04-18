#!/usr/bin python3
# @Module  : messaging
# @File    : log_service.py
# @Time    : 2024-04-17 15:21:21
# @Author  : Kelvin.Ye
from app.modules.messaging.model import TNoticeLog
from app.tools.service import http_service
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import TIMEFMT


@http_service
def query_notice_log_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.equal(TNoticeLog.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TNoticeLog.LOG_NO, req.logNo)
    conds.equal(TNoticeLog.EVENT, req.event)
    conds.equal(TNoticeLog.CHANNEL, req.channel)
    conds.equal(TNoticeLog.SUCCESS, req.success)
    conds.ge(TNoticeLog.CREATED_TIME, req.startTime)
    conds.le(TNoticeLog.CREATED_TIME, req.endTime)

    # 查询日志列表
    pagination = (
        TNoticeLog
        .filter(*conds)
        .order_by(TNoticeLog.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'logNo': entity.LOG_NO,
            'event': entity.EVENT,
            'channel': entity.CHANNEL,
            'content': entity.CONTENT,
            'success': entity.SUCCESS,
            'notifiedTime': entity.CREATED_TIME.strftime(TIMEFMT)
        }
        for entity in pagination.items
    ]

    return {'list': data, 'total': pagination.total}
