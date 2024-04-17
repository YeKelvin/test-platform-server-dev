#!/usr/bin/ python3
# @File    : notice_controller.py
# @Time    : 2022-05-07 22:32:14
# @Author  : Kelvin.Ye
from app.modules.messaging.controller import blueprint
from app.modules.messaging.enum import NoticeBotState
from app.modules.messaging.enum import NoticeBotType
from app.modules.messaging.service import notice_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/notice/bot/list')
@require_login
@require_permission
def query_notice_bot_list(CODE='QUERY_NOTICE_BOT'):
    """分页查询通知机器人列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('botNo'),
        Argument('botName'),
        Argument('botDesc'),
        Argument('botType'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_notice_bot_list(req)


@blueprint.get('/notice/bot/all')
@require_login
@require_permission
def query_notice_bot_all(CODE='QUERY_NOTICE_BOT'):
    """查询全部通知机器人"""
    req = JsonParser(
        Argument('workspaceNo')
    ).parse()
    return service.query_notice_bot_all(req)


@blueprint.get('/notice/bot')
@require_login
@require_permission
def query_notice_bot(CODE='QUERY_NOTICE_BOT'):
    """查询通知机器人"""
    req = JsonParser(
        Argument('botNo', required=True, nullable=False, help='机器人编号不能为空')
    ).parse()
    return service.query_notice_bot(req)


@blueprint.post('/notice/bot')
@require_login
@require_permission
def create_notice_bot(CODE='CREATE_NOTICE_BOT'):
    """新增通知机器人"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('botName', required=True, nullable=False, help='机器人名称不能为空'),
        Argument('botDesc'),
        Argument('botType', required=True, nullable=False, enum=NoticeBotType, help='机器人类型不能为空'),
        Argument('botSecret'),
        Argument('botWebhook', required=True, nullable=False, help='机器人Webhook地址不能为空'),
        Argument('botMentions', type=list)
    ).parse()
    return service.create_notice_bot(req)


@blueprint.put('/notice/bot')
@require_login
@require_permission
def modify_notice_bot(CODE='MODIFY_NOTICE_BOT'):
    """修改通知机器人"""
    req = JsonParser(
        Argument('botNo', required=True, nullable=False, help='机器人编号不能为空'),
        Argument('botName', required=True, nullable=False, help='机器人名称不能为空'),
        Argument('botDesc'),
        Argument('botSecret'),
        Argument('botWebhook', required=True, nullable=False, help='机器人Webhook地址不能为空'),
        Argument('botMentions', type=list)
    ).parse()
    return service.modify_notice_bot(req)


@blueprint.put('/notice/bot/state')
@require_login
@require_permission
def modify_notice_bot_state(CODE='MODIFY_NOTICE_BOT'):
    """修改通知机器人状态"""
    req = JsonParser(
        Argument('botNo', required=True, nullable=False, help='机器人编号不能为空'),
        Argument('state', required=True, nullable=False, enum=NoticeBotState, help='通知机器人状态不能为空')
    ).parse()
    return service.modify_notice_bot_state(req)


@blueprint.delete('/notice/bot')
@require_login
@require_permission
def remove_notice_bot(CODE='REMOVE_NOTICE_BOT'):
    """删除通知机器人"""
    req = JsonParser(
        Argument('botNo', required=True, nullable=False, help='机器人编号不能为空')
    ).parse()
    return service.remove_notice_bot(req)
