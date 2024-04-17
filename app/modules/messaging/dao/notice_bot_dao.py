#!/usr/bin/ python3
# @File    : notice_bot_dao.py
# @Time    : 2022-05-07 22:32:45
# @Author  : Kelvin.Ye
from app.modules.messaging.model import TNoticeBot


def select_first(**kwargs) -> TNoticeBot:
    return TNoticeBot.filter_by(**kwargs).first()


def select_by_no(bot_no) -> TNoticeBot:
    return TNoticeBot.filter_by(BOT_NO=bot_no).first()


def select_by_name(bot_name) -> TNoticeBot:
    return TNoticeBot.filter_by(BOT_NAME=bot_name).first()


def select_by_name_and_type(bot_name, bot_type) -> TNoticeBot:
    return TNoticeBot.filter_by(BOT_NAME=bot_name, BOT_TYPE=bot_type).first()
