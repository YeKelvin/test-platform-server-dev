#!/usr/bin python3
# @Module  : signals
# @File    : notice_reveiver.py
# @Time    : 2024-04-17 16:03:00
# @Author  : Kelvin.Ye
from loguru import logger

from app.extension import db
from app.modules.messaging.dao import notice_bot_dao
from app.modules.messaging.model import TNoticeBot
from app.modules.messaging.model import TNoticeLog
from app.signals import notice_signal
from app.tools.exceptions import NoticeError
from app.tools.localvars import get_trace_id
from app.utils.notice import wecom as wecom_notice


@notice_signal.connect
def notify_by_bot(sender, bot_no, event, *, text:str=None, markdown:str=None):
    bot = notice_bot_dao.select_by_no(bot_no)
    if not bot:
        logger.warning(f'通知BOT:[ {bot_no} ] 查询机器人失败')
        return
    if bot.STATE != 'ENABLE':
        logger.warning(f'通知BOT:[ {bot.BOT_NAME} ] 机器人状态异常')
        return

    # 发送通知
    success = True
    try:
        if bot.BOT_TYPE == 'WECOM':
            notify_wecom_bot(bot, text=text, markdown=markdown)
        elif bot.BOT_TYPE == 'DINGTALK':
            notify_dingtalk_bot(bot, text=text, markdown=markdown)
        elif bot.BOT_TYPE == 'FEISHU':
            notify_feishu_bot(bot, text=text, markdown=markdown)
        else:
            logger.warning(f'通知BOT:[ {bot.BOT_TYPE} ] 不支持的通知渠道')
            return
    except NoticeError:
        success = False
    except Exception:
        success = False
        logger.exception(f'通知BOT:[ {bot.BOT_NAME} ] 发送异常')

    # 记录通知日志
    TNoticeLog.insert(
        WORKSPACE_NO = bot.WORKSPACE_NO,
        LOG_NO = get_trace_id(),
        EVENT = event,
        CHANNEL = bot.BOT_TYPE,
        CONTENT = text or markdown,
        MENTIONS = bot.BOT_MENTIONS,
        SUCCESS = success
    )
    # 这里可能要手动提交
    db.session.commit()


def notify_wecom_bot(bot: TNoticeBot, *, text: str = None, markdown: str = None):
    if text is None and markdown is None:
        raise NoticeError('通知内容不能为空')

    if text:
        wecom_notice.send_text(bot.BOT_WEBHOOK, text)
        return
    if markdown:
        wecom_notice.send_markdown(bot.BOT_WEBHOOK, markdown)
        return


def notify_dingtalk_bot(bot: TNoticeBot, *, text: str = None, markdown: str = None):
    pass


def notify_feishu_bot(bot: TNoticeBot, *, text: str = None, markdown: str = None):
    pass
