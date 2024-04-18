#!/usr/bin python3
# @Module  : messaging
# @File    : log_controller.py
# @Time    : 2024-04-17 15:21:39
# @Author  : Kelvin.Ye
from app.modules.messaging.controller import blueprint
from app.modules.messaging.service import log_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/notice/log/list')
@require_login
@require_permission
def query_notice_log_list(CODE='QUERY_LOG'):
    """分页查询通知日志列表"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('logNo'),
        Argument('event'),
        Argument('channel'),
        Argument('success'),
        Argument('startTime'),
        Argument('endTime'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_notice_log_list(req)
