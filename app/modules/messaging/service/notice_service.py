#!/usr/bin/ python3
# @File    : notice_service.py
# @Time    : 2022-05-07 22:32:17
# @Author  : Kelvin.Ye
from app.modules.messaging.dao import notice_bot_dao
from app.modules.messaging.enum import NoticeBotState
from app.modules.messaging.model import TNoticeBot
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_absent
from app.tools.validator import check_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_notice_bot_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.like(TNoticeBot.WORKSPACE_NO, req.workspaceNo)
    conds.like(TNoticeBot.BOT_NO, req.botNo)
    conds.like(TNoticeBot.BOT_NAME, req.botName)
    conds.like(TNoticeBot.BOT_DESC, req.botDesc)
    conds.like(TNoticeBot.BOT_TYPE, req.botType)
    conds.like(TNoticeBot.STATE, req.state)

    # 查询机器人列表
    pagination = (
        TNoticeBot
        .filter(*conds)
        .order_by(TNoticeBot.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'botNo': bot.BOT_NO,
            'botName': bot.BOT_NAME,
            'botDesc': bot.BOT_DESC,
            'botType': bot.BOT_TYPE,
            'state': bot.STATE
        }
        for bot in pagination.items
    ]

    return {'list': data, 'total': pagination.total}


@http_service
def query_notice_bot_all(req):
    # 查询所有机器人
    conds = QueryCondition()
    conds.equal(TNoticeBot.WORKSPACE_NO, req.workspaceNo)
    bots = TNoticeBot.filter(*conds).order_by(TNoticeBot.CREATED_TIME.desc()).all()

    return [
        {
            'botNo': bot.BOT_NO,
            'botName': bot.BOT_NAME,
            'botDesc': bot.BOT_DESC,
            'botType': bot.BOT_TYPE,
            'state': bot.STATE
        }
        for bot in bots
    ]


@http_service
def query_notice_bot(req):
    # 查询机器人
    bot = notice_bot_dao.select_by_no(req.botNo)
    check_exists(bot, error='机器人不存在')

    return {
        'workspaceNo': bot.WORKSPACE_NO,
        'botNo': bot.BOT_NO,
        'botName': bot.BOT_NAME,
        'botDesc': bot.BOT_DESC,
        'botType': bot.BOT_TYPE,
        'botSecret': bot.BOT_SECRET,
        'botWebhook': bot.BOT_WEBHOOK,
        'botMentions': bot.BOT_MENTIONS,
        'state': bot.STATE
    }


@http_service
def create_notice_bot(req):
    # 空间编号不能为空
    if not req.workspaceNo:
        raise ServiceError(msg='空间编号不能为空')

    # 查询机器人
    bot = notice_bot_dao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        BOT_NAME=req.botName,
        BOT_TYPE=req.botType
    )
    check_absent(bot, error='机器人已存在')

    # 新增机器人
    bot_no = new_id()
    TNoticeBot.insert(
        WORKSPACE_NO=req.workspaceNo,
        BOT_NO=bot_no,
        BOT_NAME=req.botName,
        BOT_DESC=req.botDesc,
        BOT_TYPE=req.botType,
        BOT_SECRET=req.botSecret,
        BOT_WEBHOOK=req.botWebhook,
        BOT_MENTIONS=req.botMentions,
        STATE=NoticeBotState.ENABLE.value
    )

    return {'botNo': bot_no}


@http_service
def modify_notice_bot(req):
    # 查询机器人
    bot = notice_bot_dao.select_by_no(req.botNo)
    check_exists(bot, error='机器人不存在')

    # 唯一性校验
    if bot.BOT_NAME != req.botName and notice_bot_dao.select_first(
        WORKSPACE_NO=bot.WORKSPACE_NO,
        BOT_NAME=req.botName,
        BOT_TYPE=bot.BOT_TYPE
    ):
        raise ServiceError(msg='机器人名称已存在')

    # 更新机器人信息
    bot.update(
        BOT_NAME=req.botName,
        BOT_DESC=req.botDesc,
        BOT_SECRET=req.botSecret,
        BOT_WEBHOOK=req.botWebhook,
        BOT_MENTIONS=req.botMentions
    )


@http_service
def modify_notice_bot_state(req):
    # 查询机器人
    bot = notice_bot_dao.select_by_no(req.botNo)
    check_exists(bot, error='机器人不存在')

    # 更新机器人状态
    bot.update(STATE=req.state)


@http_service
def remove_notice_bot(req):
    # 查询机器人
    bot = notice_bot_dao.select_by_no(req.botNo)
    check_exists(bot, error='机器人不存在')

    # 删除机器人
    bot.delete()
