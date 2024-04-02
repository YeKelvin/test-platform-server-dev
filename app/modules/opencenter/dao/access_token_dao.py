#!/usr/bin python3
# @Module  : opencenter.dao
# @File    : access_token_dao.py
# @Time    : 2024-04-02 11:46:55
# @Author  : Kelvin.Ye
from app.modules.opencenter.model import TAccessToken


def select_by_no(token_no) -> TAccessToken:
    return TAccessToken.filter_by(TOKEN_NO=token_no).first()
