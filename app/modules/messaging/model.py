#!/usr/bin python3
# @Module  : messaging
# @File    : model.py
# @Time    : 2024-04-17 11:46:46
# @Author  : Kelvin.Ye
from sqlalchemy.dialects.postgresql import JSONB

from app.database import BaseColumn
from app.database import TableModel
from app.database import db


class TNoticeBot(TableModel, BaseColumn):
    """通知机器人表"""
    __tablename__ = 'NOTICE_BOT'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    BOT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='机器人编号')
    BOT_NAME = db.Column(db.String(128), nullable=False, comment='机器人名称')
    BOT_DESC = db.Column(db.String(256), comment='机器人描述')
    BOT_TYPE = db.Column(db.String(16), nullable=False, comment='机器人类型(WECOM, DINGTALK, FEISHU)')
    BOT_SECRET = db.Column(db.String(128), comment='机器人加签密钥')
    BOT_WEBHOOK = db.Column(db.String(256), comment='机器人webhook地址')
    BOT_MENTIONS = db.Column(JSONB, comment='机器人提及用户列表')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='机器人状态(ENABLE:启用, DISABLE:禁用)')


class TNoticeLog(TableModel, BaseColumn):
    """通知日志表"""
    __tablename__ = 'NOTICE_LOG'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    LOG_NO = db.Column(db.String(32), index=True, nullable=False, comment='日志编号')
    EVENT = db.Column(db.String(64), nullable=False, comment='触发事件')
    CHANNEL = db.Column(db.String(16), nullable=False, comment='通知渠道')
    CONTENT = db.Column(db.Text(), nullable=False, comment='通知内容')
    MENTIONS = db.Column(JSONB, comment='通知提醒人')
    SUCCESS = db.Column(db.Boolean(), comment='发送成功')
