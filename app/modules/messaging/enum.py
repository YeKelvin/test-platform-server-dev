#!/usr/bin python3
# @Module  : messaging
# @File    : model.py
# @Time    : 2024-04-17 11:46:46
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


@unique
class NoticeBotState(Enum):
    # 启用
    ENABLE = 'ENABLE'
    # 禁用
    DISABLE = 'DISABLE'


@unique
class NoticeBotType(Enum):
    # 企业微信
    WECOM = 'WECOM'
    # 钉钉
    DINGTALK = 'DINGTALK'
    # 飞书
    FEISHU = 'FEISHU'


@unique
class NoticeEvent(Enum):
    # 测试计划执行完成
    TESTPLAN_EXECUTION_COMPLETED = 'TESTPLAN_EXECUTION_COMPLETED'
