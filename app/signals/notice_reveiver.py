#!/usr/bin python3
# @Module  : signals
# @File    : notice_reveiver.py
# @Time    : 2024-04-17 16:03:00
# @Author  : Kelvin.Ye
from app.signals import notice_signal


@notice_signal.connect
def notify_by_bot(sender, bot_no, conent):
    pass
